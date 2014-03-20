from setuptools import setup, find_packages
import pkgutil

phonenumbers_installed = filter(lambda p: p[1] == 'phonenumbers', 
                                pkgutil.iter_modules())

setup(
    name="django-phonenumber-field",
    version = ":versiontools:phonenumber_field:",
    url='http://github.com/stefanfoulis/django-phonenumber-field',
    license='BSD',
    platforms=['OS Independent'],
    description="An international phone number field for django models.",
    setup_requires = [
        'versiontools >= 1.4',
    ],
    install_requires = [
        'phonenumberslite>=6.0.0a' if not phonenumbers_installed else '',
    ],
    long_description=open('README.rst').read(),
    author='Stefan Foulis',
    author_email='stefan.foulis@gmail.com',
    maintainer='Stefan Foulis',
    maintainer_email='stefan.foulis@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
