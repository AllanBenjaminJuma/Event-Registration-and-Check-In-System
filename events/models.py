from io import BytesIO
import uuid
import qrcode

from django.db import models
from django.core.files import File
from django.utils import timezone


class Event(models.Model):

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    date = models.DateTimeField()
    capacity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Registration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    signature = models.TextField(blank=True, null=True)

    facility_name = models.CharField(max_length=100, blank=True, null=True)

    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    is_checked_in = models.BooleanField(default=False)
    checked_in_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['event', 'email'], name='unique_event_email'),
            models.UniqueConstraint(fields=['event', 'phone'], name='unique_event_phone'),
        ]

    def __str__(self):
        return f"{self.name} - {self.event.title}"