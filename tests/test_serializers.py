from django.test import SimpleTestCase
from rest_framework import serializers

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
