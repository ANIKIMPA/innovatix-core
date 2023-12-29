from django.conf import settings

from core.services.payment_gateways import StripePaymentGateway

payment_gateway = StripePaymentGateway(settings.STRIPE_SECRET_KEY)
