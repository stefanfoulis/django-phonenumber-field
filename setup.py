# -*- coding: utf-8 -*-
from setuptools import setup

from phonenumber_field import __version__

setup(
    name="django-phonenumber-field",
    version=__version__,
    url="https://github.com/stefanfoulis/django-phonenumber-field",
    license="BSD",
    platforms=["OS Independent"],
    description="An international phone number field for django models.",
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    install_requires=["Django>=1.11.3", "babel"],
    extras_require={
        "phonenumbers": ["phonenumbers>=7.0.2"],
        "phonenumberslite": ["phonenumberslite>=7.0.2"],
    },
    long_description=open("README.rst").read(),
    author="Stefan Foulis",
    author_email="stefan@foulis.ch",
    maintainer="Stefan Foulis",
    maintainer_email="stefan@foulis.ch",
    packages=["phonenumber_field"],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Django",
        "Framework :: Django :: 1.11",
        "Framework :: Django :: 2.0",
        "Framework :: Django :: 2.1",
        "Framework :: Django :: 2.2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Internet :: WWW/HTTP",
    ],
)
