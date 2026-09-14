from django.db import models

# Create your models here.
class Organisation(models.Model):

    # An organisation with its users, events, registration, payments etc

    name = models.CharField(max_length=255, unique =True)

    code = models.CharField(max_length=50, unique=True, help_text="Unique code for the organisation")

    email = models.EmailField(max_length=255, unique=True, null=True, help_text="Email address of the organisation")

    address = models.TextField(blank = True, null=True, help_text="Address of the organisation")

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name