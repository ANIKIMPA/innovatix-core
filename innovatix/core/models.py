from django.db import models


class ProcessedEvent(models.Model):
    event_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed = models.BooleanField(default=False)
    event_type = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Event {self.event_id} processed: {self.processed}"
