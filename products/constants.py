from django.utils.translation import gettext_lazy as _

DAY = "day"
WEEK = "week"
MONTH = "month"
YEAR = "year"


RECURRING_INTERVAL_CHOICES = [
    (DAY, _("Daily")),
    (WEEK, _("Weekly")),
    (MONTH, _("Monthly")),
    (YEAR, _("Annual")),
]

ENTRY_COST_HELP_TEXT = _(
    "This is the initial price charged when a new subscription is created."
)
RECURRING_PRICE_HELP_TEXT = _("This is the price charged for each recurring payment.")
RECURRING_PAYMENT_INTERVAL_HELP_TEXT = _(
    "This specifies how often the recurring payment will be charged (e.g., monthly, annually)."
)
