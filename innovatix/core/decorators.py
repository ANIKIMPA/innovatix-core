import unittest

from django.conf import settings


def skip_if_dev_environment(func):
    return unittest.skipIf(
        settings.ENVIRONMENT == "dev", "Skipping this test in dev environment"
    )(func)
