from django.test import TestCase


class BaseTestCase(TestCase):
    fixtures = ["initial.json"]
