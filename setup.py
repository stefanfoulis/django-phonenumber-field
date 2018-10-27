# -*- coding: utf-8 -*-
from phonenumber_field import __version__
from setuptools import find_packages, setup


setup(
    name="django-phonenumber-field",
    version=__version__,
    url='http://github.com/stefanfoulis/django-phonenumber-field',
    license='BSD',
    platforms=['OS Independent'],
    description="An international phone number field for django models.",
    install_requires=[
        'Django>=1.11.3',
        'babel',
    ],
    extras_require={
        'phonenumbers': ['phonenumbers>=7.0.2'],
        'phonenumberslite': ['phonenumberslite>=7.0.2'],
    },
    long_description=open('README.rst').read(),
    author='Stefan Foulis',
    author_email='stefan@foulis.ch',
    maintainer='Stefan Foulis',
    maintainer_email='stefan@foulis.ch',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
