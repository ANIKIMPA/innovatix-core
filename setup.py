from setuptools import find_packages, setup

setup(
    name="innovatix-core",
    version="0.3.1",
    install_requires=[
        "Django>=4.2.3",
        "django-summernote>=0.8.20.0",
        "phonenumbers>=8.13.17",
        "python-dateutil>=2.8.2",
        "stripe>=5.5.0",
        "django-allauth>=0.61.1",
    ],
    packages=find_packages(),
    package_data={
        "innovatix.core": ["fixtures/*.json"],
    },
)
