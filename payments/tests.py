from unittest.mock import Mock, patch

from django.test import Client
from django.urls import reverse

from innovatix.core.tests import BaseTestCase
from innovatix.geo_territories.utils import get_default_country, get_default_province
from innovatix.users.utils import (
    create_fake_customer_user,
    get_user_info_fake_session_data,
)
from payments.constants import SUCCEEDED
from payments.utils import create_fake_payment, create_fake_payment_method
from products.tests import create_fake_membership, create_fake_subscription


class PaymentMethodModelTest(BaseTestCase):
    def setUp(self):
        self.country = get_default_country()
        self.province = get_default_province()
        self.user = create_fake_customer_user(self.province, self.country)
        self.payment_method = create_fake_payment_method(self.user)

    def test_payment_method_creation(self):
        self.assertEqual(self.payment_method.user, self.user)
        self.assertEqual(self.payment_method.type, "visa")
        self.assertEqual(self.payment_method.last_four, "1234")


class PaymentModelTest(BaseTestCase):
    def setUp(self):
        self.country = get_default_country()
        self.province = get_default_province()
        self.user = create_fake_customer_user(self.province, self.country)
        self.membership = create_fake_membership()
        self.user_membership = create_fake_subscription(
            user=self.user, membership=self.membership
        )
        self.payment_method = create_fake_payment_method(self.user)
        self.payment = create_fake_payment(self.user_membership, self.payment_method)

    def test_payment_creation(self):
        self.assertEqual(self.payment.user_membership, self.user_membership)
        self.assertEqual(self.payment.payment_method, self.payment_method)
        self.assertEqual(self.payment.subtotal, 10.00)
        self.assertEqual(self.payment.tax, 0.00)
        self.assertEqual(self.payment.total, 10.00)
        self.assertEqual(self.payment.status, "completed")


class PaymentInfoPageViewTest(BaseTestCase):
    def setUp(self):
        # Initialize the Django test client
        self.client = Client()

        self.membership = create_fake_membership()
        self.url = reverse(
            "payments:payment-info", kwargs={"slug": self.membership.slug}
        )

        # Create Country and Province instances
        self.country = get_default_country()
        self.province = get_default_province()

        # Initialize session variables
        self.user_info = get_user_info_fake_session_data(self.country, self.province)
        session = self.client.session
        session["user_info"] = self.user_info
        session.save()

    def test_page_loads(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "payments/payment_info_form.html")

    def test_form_prepopulated_with_session_data(self):
        self.user_info["country"] = self.country
        self.user_info["province"] = self.province
        response = self.client.get(
            reverse("payments:payment-info", kwargs={"slug": self.membership.slug})
        )

        self.assertIn("user_info", response.context)
        self.assertEqual(response.context["user_info"], self.user_info)

    def _test_response(
        self,
        mock_create_confirm_subscription,
        mock_create_customer,
        expected_status_code,
    ):
        form_data = {
            "card_name": "Test Example",
            "payment_method_id": "pm_testpaymentmethodid1",
        }
        response = self.client.post(
            reverse("payments:payment-info", kwargs={"slug": self.membership.slug}),
            data=form_data,
        )

        self.assertEqual(response.status_code, expected_status_code)
        mock_create_customer.assert_called()
        mock_create_confirm_subscription.assert_called()

        return response

    @patch(
        "products.services.payment_gateway.create_customer",
        return_value=Mock(id="customer_id"),
    )
    @patch(
        "products.services.payment_gateway.create_confirm_subscription",
        return_value={"code": SUCCEEDED},
    )
    def test_valid_response(
        self, mock_create_confirm_subscription, mock_create_customer
    ):
        response = self._test_response(
            mock_create_confirm_subscription, mock_create_customer, 302
        )
        self.assertRedirects(
            response, reverse("payments:payment-success"), response.status_code, 200
        )

    @patch(
        "products.services.payment_gateway.create_customer",
        return_value=Mock(id="customer_id"),
    )
    @patch(
        "products.services.payment_gateway.create_confirm_subscription",
        return_value={"code": "error", "error": {"message": "Test error message"}},
    )
    def test_invalid_response(
        self, mock_create_confirm_subscription, mock_create_customer
    ):
        response = self._test_response(
            mock_create_confirm_subscription, mock_create_customer, 200
        )
        self.assertContains(response, "Test error message")

    @patch(
        "products.services.payment_gateway.create_customer",
        return_value=Mock(id="customer_id"),
    )
    @patch(
        "products.services.payment_gateway.create_confirm_subscription",
        return_value={"code": SUCCEEDED},
    )
    @patch("payments.views.CustomerUserForm")
    def test_invalid_user_info_redirects(
        self,
        MockCustomerUserForm,
        mock_create_confirm_subscription,
        mock_create_customer,
    ):
        mock_form_instance = Mock()
        mock_form_instance.is_valid.return_value = False
        MockCustomerUserForm.return_value = mock_form_instance

        form_data = {
            "card_name": "Test Example",
            "payment_method_id": "pm_testpaymentmethodid1",
        }

        response = self.client.post(
            reverse("payments:payment-info", kwargs={"slug": self.membership.slug}),
            data=form_data,
        )

        # Asserting that it redirects to the 'users:customer-info' URL
        self.assertRedirects(
            response, reverse("users:customer-info", args=[str(self.membership.slug)])
        )

        # Asserting that the status code is 302 (redirect)
        self.assertEqual(response.status_code, 302)

        mock_create_customer.assert_not_called()
        mock_create_confirm_subscription.assert_not_called()
