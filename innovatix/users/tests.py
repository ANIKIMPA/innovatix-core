from django.contrib.admin.models import LogEntry
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from innovatix.core.tests import BaseTestCase
from innovatix.geo_territories.utils import get_default_country, get_default_province
from innovatix.users.forms import ContactForm
from innovatix.users.models import ContactModel, CustomerUser
from innovatix.users.utils import create_fake_contact, create_fake_customer_user


class ContactFormViewTest(BaseTestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("users:contact")

    def test_get_request(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/contact.html")

    def test_post_request_with_valid_data(self):
        data = {
            "name": "Test",
            "email": "test@example.com",
            "phone_number": "9393316860",
            "message": "Hello",
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 302)  # Check for redirect
        self.assertRedirects(
            response, reverse("home")
        )  # Assuming 'home' is the name of the url for the home page
        # Check that a ContactModel instance has been created
        self.assertEqual(ContactModel.objects.filter(name="Test").count(), 1)
        # Check that a log entry has been created
        self.assertEqual(
            LogEntry.objects.filter(object_repr="Test (test@example.com)").count(), 1
        )

    def test_post_request_with_invalid_data(self):
        data = {
            "name": "",
            "email": "not an email",
            "phone_number": "1234567890",
            "message": "Hello",
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 200)  # No redirect should occur
        # Check that no ContactModel instance has been created
        self.assertEqual(ContactModel.objects.filter(name="").count(), 0)


class ContactFormTest(TestCase):
    def setUp(self) -> None:
        self.data = {
            "name": "Test",
            "email": "test@example.com",
            "phone_number": "9393316860",
            "message": "Hello",
        }

    def test_form_with_valid_data(self):
        form = ContactForm(self.data)
        self.assertTrue(form.is_valid())

    def test_form_with_no_name(self):
        self.data["name"] = ""
        form = ContactForm(self.data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["name"], ["This field is required."])

    def test_form_with_invalid_email(self):
        self.data["email"] = "not an email"
        form = ContactForm(self.data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["email"], ["Enter a valid email address."])

    def test_form_with_no_phone_number(self):
        self.data["phone_number"] = ""
        form = ContactForm(self.data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["phone_number"], ["This field is required."])

    def test_form_with_invalid_phone_number(self):
        self.data["phone_number"] = "1234567890"
        form = ContactForm(self.data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["phone_number"], ["The phone number entered is not valid."]
        )

    def test_form_with_no_message(self):
        self.data["message"] = ""
        form = ContactForm(self.data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["message"], ["This field is required."])


class ContactModelTest(TestCase):
    def setUp(self) -> None:
        self.contact = create_fake_contact()

    def test_create_contact_model(self):
        self.assertEqual(ContactModel.objects.count(), 1)
        self.assertEqual(ContactModel.objects.first(), self.contact)


class CustomerUserTest(BaseTestCase):
    def setUp(self):
        # Create instances of Country and Province for testing
        self.country = get_default_country()
        self.province = get_default_province()
        self.customer_user = create_fake_customer_user(self.province, self.country)

    def test_create_customer_user(self):
        self.assertIsInstance(self.customer_user, CustomerUser)
        self.assertTrue(self.customer_user.check_password("thepassword"))

    def test_generate_partner_number_on_create(self):
        self.assertIsNotNone(self.customer_user.partner_number)
        self.assertRegex(self.customer_user.partner_number, r"^\d{4}-\d{2}-\d{4}$")

    def test_not_update_partner_number_on_save(self):
        old_partner_number = self.customer_user.partner_number
        self.customer_user.save()
        self.customer_user.refresh_from_db()
        self.assertEqual(self.customer_user.partner_number, old_partner_number)

    def test_partner_number_generation(self):
        # Create a CustomerUser instance
        user2 = create_fake_customer_user(
            province=self.province,
            country=self.country,
            email="user2@example.com",
            address1="Test Address 1",
        )

        # Get the current date
        current_date = timezone.now()

        # The partner_number should be '{year}-{month}-0001' since this is the first user this month
        expected_partner_number = (
            f"{current_date.year}-{str(current_date.month).zfill(2)}-0002"
        )
        self.assertEqual(user2.partner_number, expected_partner_number)

        # Create another CustomerUser instance
        user3 = create_fake_customer_user(
            province=self.province,
            country=self.country,
            email="user3@example.com",
            address1="Test Address 2",
        )

        # The partner_number should be '{year}-{month}-0002' since this is the second user this month
        expected_partner_number = (
            f"{current_date.year}-{str(current_date.month).zfill(2)}-0003"
        )
        self.assertEqual(user3.partner_number, expected_partner_number)

    def test_format_us_number(self):
        user = create_fake_customer_user(
            province=self.province,
            country=self.country,
            email="test@example.com",
            phone_number="+16502532222",
        )
        formatted_phone = user.format_phone_number()
        self.assertEqual(formatted_phone, "+1 650-253-2222")
