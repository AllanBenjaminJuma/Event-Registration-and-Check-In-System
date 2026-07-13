from django.contrib import admin
from django.contrib import admin

from .models import CheckIn, EnabledPaymentMethod, Event, Payment, Registration, EventType, TicketType,PaymentMethod
# Register your models here.

admin.site.register(Event)
admin.site.register(Registration)
admin.site.register(EventType)
admin.site.register(TicketType)
admin.site.register(PaymentMethod)
admin.site.register(CheckIn)
admin.site.register(EnabledPaymentMethod)
admin.site.register(Payment)