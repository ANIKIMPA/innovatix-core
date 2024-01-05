from setuptools import setup

setup(
    name="innovatix-core",
    version="0.2.4",
    install_requires=[
        "Django>=4.2.3",
        "django-summernote>=0.8.20.0",
        "phonenumbers>=8.13.17",
        "python-dateutil>=2.8.2",
        "stripe>=5.5.0",
    ],
)
