from django.conf import settings

from innovatix.core.services.payment_gateways import CoreStripePaymentGateway

payment_gateway = CoreStripePaymentGateway(settings.STRIPE_SECRET_KEY)
