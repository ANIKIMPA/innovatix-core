SUCCEEDED = "succeeded"
BLOCKED = "blocked"
CANCELLED = "cancelled"
PENDING = "pending"
INCOMPLETED = "incomplete"
FAILED = "failed"
REFUNDED = "refunded"
DISPUTED = "disputed"
REQUIRES_PAYMENT_METHOD = "requires_payment_method"


PAYMENT_STATUS_CHOICES = [
    (SUCCEEDED, SUCCEEDED.capitalize()),
    (BLOCKED, BLOCKED.capitalize()),
    (CANCELLED, CANCELLED.capitalize()),
    (PENDING, PENDING.capitalize()),
    (INCOMPLETED, INCOMPLETED.capitalize()),
    (FAILED, FAILED.capitalize()),
    (REFUNDED, REFUNDED.capitalize()),
    (DISPUTED, DISPUTED.capitalize()),
    (REQUIRES_PAYMENT_METHOD, "Incomplete"),
]
