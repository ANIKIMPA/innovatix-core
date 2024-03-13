from unittest.mock import patch

from django.contrib.admin.sites import AdminSite
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.exceptions import ValidationError
from django.http import HttpRequest
from django.test import TestCase
from django.urls import reverse, reverse_lazy
from innovatix.core.tests import BaseTestCase
from innovatix.geo_territories.utils import get_default_country, get_default_province
from innovatix.users.utils import create_fake_customer_user
from products.admin import UserMembershipAdmin
from products.models import UserMembership
from products.tests import create_fake_membership
from products.utils import create_fake_membership, create_fake_subscription


class MembershipModelTest(TestCase):
    def setUp(self):
        self.membership = create_fake_membership()

    def test_membership_creation(self):
        self.assertEqual(self.membership.name, "Test Membership")
        self.assertEqual(self.membership.get_recurring_price(), 10.49)

    @patch("products.models.payment_gateway.delete_membership")
    def test_delete_membership_not_linked_to_subscription(self, mock_delete_membership):
        self.membership.delete()
        mock_delete_membership.assert_called_once_with(self.membership)

    @patch("products.models.payment_gateway.delete_membership")
    def test_delete_membership_linked_to_subscription(self, mock_delete_membership):
        # Assume is_linked_to_subscriptions returns True
        self.membership.is_linked_to_subscriptions = lambda: True

        # Try to delete the membership and expect a ValidationError
        with self.assertRaises(ValidationError):
            self.membership.delete()

        mock_delete_membership.assert_not_called()


class UserMembershipModelTest(BaseTestCase):
    def setUp(self):
        self.country = get_default_country()
        self.province = get_default_province()
        self.user = create_fake_customer_user(self.province, self.country)
        self.membership = create_fake_membership()
        self.user_membership = create_fake_subscription(self.user, self.membership)

    def test_user_membership_creation(self):
        self.assertEqual(self.user_membership.user, self.user)
        self.assertEqual(self.user_membership.membership, self.membership)


class MockRequest(HttpRequest):
    pass


class MockSuperUser:
    def has_perm(self, perm):
        return True


request = MockRequest()
request.user = MockSuperUser()


class UserMembershipAdminTestCase(BaseTestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = UserMembershipAdmin(UserMembership, self.site)
        self.membership1 = create_fake_membership()
        self.membership2 = create_fake_membership(
            name="Test Membership 2",
            slug="test-membership-2",
            recurring_price=2000,
        )
        self.customer1 = create_fake_customer_user(
            get_default_province(), get_default_country()
        )
        self.customer2 = create_fake_customer_user(
            get_default_province(),
            get_default_country(),
            first_name="Customer",
            last_name="2",
            email="customer2@example.com",
        )
        self.subscription1 = create_fake_subscription(self.customer1, self.membership1)
        self.subscription2 = create_fake_subscription(self.customer2, self.membership2)

    def test_has_delete_permission(self):
        self.assertFalse(self.admin.has_delete_permission(request))

    def test_has_add_permission(self):
        self.assertFalse(self.admin.has_add_permission(request))

    def test_has_change_permission(self):
        self.assertFalse(self.admin.has_change_permission(request))

    @patch("products.services.payment_gateway.update_subscription")
    def test_update_price(self, mock_update_subscription):
        mock_update_subscription.return_value = {
            "object": "subscription",
        }
        queryset = UserMembership.objects.filter(
            id__in=[self.subscription1.pk, self.subscription2.pk]
        )

        # Mock POST data to simulate a submitted form
        request.POST = {
            "apply": "Apply",
            "new_price": "30.00",  # New price
            "new_interval": "year",  # New interval
        }

        # Required for message framework
        setattr(request, "session", "session")
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)

        # Call the update_price method
        self.admin.update_price(request, queryset)

        # Reload objects from database and check that prices were updated
        self.subscription1.refresh_from_db()
        self.subscription2.refresh_from_db()

        self.assertEqual(self.subscription1.recurring_price, 3000)  # New price in cents
        self.assertEqual(self.subscription1.recurring_payment, "year")  # New interval
        self.assertEqual(
            self.subscription2.get_recurring_price(), 30.00
        )  # New price in dollars
        self.assertEqual(self.subscription2.recurring_payment, "year")  # New interval


class CustomerInfoPageViewTest(BaseTestCase):
    def setUp(self):
        self.membership = create_fake_membership()
        self.url = reverse(
            "products:customer-info", kwargs={"slug": self.membership.slug}
        )

    def test_page_loads(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "products/customeruser_update_form.html")

    def test_valid_form_submission(self):
        response = self.client.post(self.url)

        self.assertRedirects(
            response,
            reverse_lazy(
                "payments:payment-info", kwargs={"slug": self.membership.slug}
            ),
        )
