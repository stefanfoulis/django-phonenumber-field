from setuptools import setup, find_packages
from phonenumber_field import __version__

setup(
    name="django-phonenumber-field",
    version=__version__,
    url='http://github.com/stefanfoulis/django-phonenumber-field',
    license='BSD',
    platforms=['OS Independent'],
    description="An international phone number field for django models.",
    install_requires=[
        'phonenumbers>=7.0.2',
        'babel',
    ],
    long_description=open('README.rst').read(),
    author='Stefan Foulis',
    author_email='stefan.foulis@gmail.com',
    maintainer='Stefan Foulis',
    maintainer_email='stefan.foulis@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    package_data = {
        'phonenumber_field': [
            'templates/phonenumber_field/*.html',
            'locale/*/LC_MESSAGES/*',
        ],
    },
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
