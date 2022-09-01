from django.test import SimpleTestCase, override_settings
from rest_framework import renderers, serializers

from phonenumber_field.phonenumber import PhoneNumber
from phonenumber_field.serializerfields import PhoneNumberField

from .models import OptionalPhoneNumber


class PhoneNumberSerializerTest(SimpleTestCase):
    def test_blank_field(self):
        class PhoneNumberSerializer(serializers.ModelSerializer):
            class Meta:
                model = OptionalPhoneNumber
                fields = ["phone_number"]

        for data in [{}, {"phone": ""}]:
            with self.subTest(data):
                s = PhoneNumberSerializer(data=data)
                self.assertIs(s.is_valid(), True)
                self.assertEqual(s.data, {})

    def test_int(self):
        class PhoneNumberSerializer(serializers.Serializer):
            phone = PhoneNumberField()

        s = PhoneNumberSerializer(data={"phone": 1})
        self.assertIs(s.is_valid(), False)

    def test_empty_required(self):
        class PhoneNumberSerializer(serializers.Serializer):
            phone = PhoneNumberField()

        serializer = PhoneNumberSerializer(data={"phone": ""})
        self.assertIs(serializer.is_valid(), False)
        self.assertEqual(serializer.validated_data, {})

    def test_empty_optional(self):
        class PhoneNumberSerializer(serializers.Serializer):
            phone = PhoneNumberField(allow_blank=True)

        serializer = PhoneNumberSerializer(data={"phone": ""})
        self.assertIs(serializer.is_valid(), True)
        self.assertEqual(serializer.validated_data, {"phone": ""})

    def test_e164_phone_number(self):
        class PhoneNumberSerializer(serializers.Serializer):
            phone = PhoneNumberField()

        serializer = PhoneNumberSerializer(data={"phone": "+33612345678"})
        self.assertIs(serializer.is_valid(), True)
        self.assertEqual(serializer.validated_data, {"phone": "+33612345678"})
        self.assertIsInstance(serializer.validated_data["phone"], PhoneNumber)

    def test_region(self):
        class PhoneNumberSerializer(serializers.Serializer):
            phone = PhoneNumberField(region="FR")

        serializer = PhoneNumberSerializer(data={"phone": "0612345678"})
        self.assertIs(serializer.is_valid(), True)
        self.assertEqual(serializer.validated_data, {"phone": "+33612345678"})
        self.assertIsInstance(serializer.validated_data["phone"], PhoneNumber)

    def test_region_invalid(self):
        class PhoneNumberSerializer(serializers.Serializer):
            phone = PhoneNumberField(region="GB")

        serializer = PhoneNumberSerializer(data={"phone": "0612345678"})
        self.assertIs(serializer.is_valid(), False)
        self.assertEqual(serializer.validated_data, {})
        self.assertEqual(serializer.errors, {"phone": ["Enter a valid phone number."]})

    @override_settings(PHONENUMBER_DEFAULT_REGION="FR")
    def test_region_from_settings(self):
        class PhoneNumberSerializer(serializers.Serializer):
            phone = PhoneNumberField()

        serializer = PhoneNumberSerializer(data={"phone": "0612345678"})
        self.assertIs(serializer.is_valid(), True)
        self.assertEqual(serializer.validated_data, {"phone": "+33612345678"})
        self.assertIsInstance(serializer.validated_data["phone"], PhoneNumber)

    @override_settings(PHONENUMBER_DEFAULT_REGION="GB")
    def test_region_kwarg_precedes_setting(self):
        class PhoneNumberSerializer(serializers.Serializer):
            phone = PhoneNumberField(region="FR")

        serializer = PhoneNumberSerializer(data={"phone": "0612345678"})
        self.assertIs(serializer.is_valid(), True)
        self.assertEqual(serializer.validated_data, {"phone": "+33612345678"})
        self.assertIsInstance(serializer.validated_data["phone"], PhoneNumber)

    def test_invalid_region(self):
        with self.assertRaisesMessage(
            ValueError, "“INVALID” is not a valid region code. Choices are"
        ):

            class PhoneNumberSerializer(serializers.Serializer):
                phone = PhoneNumberField(region="INVALID")

    def test_multiple_isvalid_calls(self):
        class PhoneNumberSerializer(serializers.Serializer):
            phone = PhoneNumberField()

        serializer = PhoneNumberSerializer(data={"phone": "+33612345678"})
        self.assertIs(serializer.is_valid(), True)
        self.assertIs(serializer.is_valid(), True)

    def test_serialization(self):
        class PhoneNumberSerializer(serializers.Serializer):
            phone = PhoneNumberField(region="FR")

        for fmt, expected in [
            ("E164", b"+33612345678"),
            ("INTERNATIONAL", b"+33 6 12 34 56 78"),
            ("RFC3966", b"tel:+33-6-12-34-56-78"),
        ]:
            with override_settings(PHONENUMBER_DEFAULT_FORMAT=fmt), self.subTest(fmt):
                serializer = PhoneNumberSerializer(data={"phone": "0612345678"})
                serializer.is_valid()
                self.assertEqual(
                    b'{"phone":"%b"}' % expected,
                    renderers.JSONRenderer().render(serializer.data),
                )
