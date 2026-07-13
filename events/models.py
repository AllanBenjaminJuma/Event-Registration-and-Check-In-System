from io import BytesIO
import uuid
import qrcode

from django.db import models
from django.core.files import File
from django.utils import timezone

from django.core.exceptions import ValidationError

from django.conf import settings


class EventType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    icon = models.CharField(
        max_length=50,
        default="event",
        help_text="Material Symbols icon name",
        null = True
    )

    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def sold(self):
        return self.registrations.count()
    
    @property
    def confirmed_registrations(self):

        """
        Returns the number of registrations that have been confirmed (i.e., paid if required).
        """

        return self.registrations.filter(
            payments__status="completed"
        ).distinct().count()
    
    def clean(self):

        """
        Validate event dates"""

        if self.start_date > self.end_date:
            raise ValidationError("Start date cannot be later than end date.")
        
        if self.end_date < self.start_date:
            raise ValidationError("End date cannot be earlier than start date.")
        
        if self.registration_opens and self.registration_closes:
            if self.registration_opens > self.registration_closes:
                raise ValidationError("Registration opens date cannot be later than registration closes date.")
            
            if self.registration_closes < self.registration_opens:
                raise ValidationError("Registration closes date cannot be earlier than registration opens date.")
            

    def __str__(self):
        return self.name

class Event(models.Model):

    ATTENDANCE_MODES=[
        ('single', 'Single Check-in'),
        ('daily', 'Daily Check-in'),
    ]

    uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    REGISTRATION_TYPES = [
        ('free', 'Free'),
        ('paid', 'Paid'),
    ]

    CHECKIN_MODES = [
    ("staff_only", "Staff Only"),
    ("self_only", "Self Check-In Only"),
    ("both", "Staff + Self Check-In"),
]


    title = models.CharField(max_length=200)

    description = models.TextField()

    # Dynamic Event Type
    event_type = models.ForeignKey(
        EventType,
        on_delete=models.PROTECT,
        related_name='events'
    )

    location = models.CharField(max_length=200)

    start_date = models.DateTimeField(
        null=True,
        blank=True
    )

    end_date = models.DateTimeField(
        null=True,
        blank=True
    )

    registration_opens = models.DateTimeField(
        null= True,
        blank=True
    )

    registration_closes = models.DateTimeField(
        null=True,
        blank=True
    )

    capacity = models.PositiveIntegerField(
        default=1,
    )

    registration_type = models.CharField(
        max_length=10,
        choices=REGISTRATION_TYPES,
        default='free'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    checkin_mode = models.CharField(
    max_length=20,
    choices=CHECKIN_MODES,
    default="staff_only"
    )

    attendance_mode = models.CharField(
        max_length=10,
        choices=ATTENDANCE_MODES,
        default="single"
    )


    @property
    def duration(self):

        if self.start_date and self.end_date:

            duration = self.end_date - self.start_date

            days = duration.days

            hours, remainder = divmod(
                duration.seconds,
                3600
            )

            minutes, _ = divmod(
                remainder,
                60
            )

            return f"{days}d {hours}h {minutes}m"

        return "N/A"

    @property
    def status(self):

        now = timezone.now()

        if not self.start_date or not self.end_date:
            return "Unknown"

        if now < self.start_date:
                
                return "Upcoming"
               

        if self.start_date <= now <= self.end_date:
                
                remaining = self.end_date - now

                if remaining.total_seconds() > 21600:
                     
                     return "Live"

                return "In-Progress"


        return "Finished"

    @property
    def registration_status(self):
         
         now = timezone.now()

         if self.registration_opens and now <self.registration_opens:
             return "Registration Not Open"
         
         if self.registration_closes and now > self.registration_closes:
                return "Registration Closed"
         
         return "Registration Open"


    def __str__(self):
        return self.title

# the different ticket types for an event
class TicketType(models.Model):
     
     """
    Different ticket categories available for an event.

    Example:
        - VIP
        - Regular
        - Student
        - Early Bird
    """
     
    #  one to many reltionship with Event model as event might have many ticket types
     event = models.ForeignKey(
          Event,
          on_delete=models.CASCADE,
            related_name='ticket_types'
     )

     name = models.CharField(max_length=100)
     
     description = models.TextField(blank=True, null=True)

     amount = models.DecimalField(
          max_digits=10,decimal_places=2,default=0.00
     )
     quantity = models.PositiveIntegerField(default=0, help_text="Total number of tickets available.")

     sold = models.PositiveIntegerField(default=0, help_text="Total number of tickets sold.")
     
     is_active = models.BooleanField(default=True, help_text="Indicates whether the ticket type is active or not.")

     created_at = models.DateTimeField(auto_now_add=True)


     @property
     def remaining_tickets(self):
          """
        Returns the number of tickets still available.

        Example:
            Quantity = 100
            Sold = 35

            Remaining = 65
        """
         
          return self.quantity - self.sold
     @property
     def is_sold_out(self):
        """
        Returns True if there are no tickets remaining.
        """

        return self.remaining_tickets <= 0
     
     @property
     def is_free(self):
        """
        Returns True when this ticket costs nothing.
        """

        return self.amount == 0
    
def clean(self):
     """
     Ensure that the ticket type's event is active and that the amount is non-negative."""
     if self.quantity < 0:
         raise ValidationError("Quantity cannot be negative.")
     
     if self.amount < 0:
        raise ValidationError("Amount cannot be negative.")

     def __str__(self):
          return f"{self.event.title} - {self.name}"

class Registration(models.Model):
    """
    Stores an attendee's registration for an event.

    Every registration belongs to one Event and one Ticket Type

    We store both relationships because:

    - Reports are generated per event.
    - One attendee should only register once per event.
    - Ticket prices may change later.
    - It simplifies reporting and querying.
    """

    # Event being attended.
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="registrations"
    )

    # Ticket selected by the attendee.
    ticket_type = models.ForeignKey(
        TicketType,
        on_delete=models.PROTECT,
        related_name="registrations"
    )


    name = models.CharField(max_length=100)

    email = models.EmailField()

    phone = models.CharField(max_length=20)

    facility_name = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    signature = models.TextField(
        blank=True,
        null=True
    )



    # Snapshot of the ticket price at the time the attendee registered.
    #
    # if organiser changes the ticket price, this value never changes.
    registration_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )


    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    qr_code = models.ImageField(
        upload_to="qr_codes/",
        blank=True,
        null=True
    )


    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        constraints = [

            # Prevent duplicate registrations using the same email for one event.
            models.UniqueConstraint(
                fields=["event", "email"],
                name="unique_event_email"
            ),

            # Prevent duplicate registrations using the same phone number for one event.
            models.UniqueConstraint(
                fields=["event", "phone"],
                name="unique_event_phone"
            ),
        ]


    def clean(self):
        """
        Ensure the selected ticket belongs
        to the selected event.
        """

        if self.ticket_type.event != self.event:
            raise ValidationError(
                "Selected ticket type does not belong to the selected event."
            )
        if self.ticket_type.is_sold_out:
            raise ValidationError(
                "Selected ticket type is sold out."
            )
        


    def save(self, *args, **kwargs):
        """
        Automatically copy the ticket price into the registration when it is first created.

        This keeps historical payment reports accurate.
        """

        if not self.pk:
            self.registration_amount = self.ticket_type.amount

        # Run model validation.
        self.full_clean()

        super().save(*args, **kwargs)

    @property
    def requires_payment(self):
        """
        Returns True if this registration
        requires payment.
        """

        return self.registration_amount > 0

    @property
    def is_paid(self):
        """
        Returns True when at least one payment
        has been completed.
        """

        return self.payments.filter(
            status="completed"
        ).exists()
    
    @property
    def can_check_in(self):
        """
        Determins whether the attendee can check in for the event."""

        if self.requires_payment:
            return self.is_paid
        return True

    def __str__(self):
        return f"{self.name} - {self.event.title}"

class PaymentMethod(models.Model):
    """
    Master list of payment methods supported by the system.
    """

    PAYMENT_TYPES = [
        ("mobile_money", "Mobile Money"),
        ("card", "Card"),
        ("bank_transfer", "Bank Transfer"),
        ("paypal", "PayPal"),
        ("cash", "Cash"),
        ("other", "Other"),
    ]

    name = models.CharField(
        max_length=50,
        unique=True
    )

    payment_type = models.CharField(
        max_length=20,
        choices=PAYMENT_TYPES
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name

class EnabledPaymentMethod(models.Model):
    """
    Represents the payment methods available for a specific event.
    """

    # the event that the payment is for
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='event_payment_methods'
    )

    # payment method that is enabled for an event 
    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.PROTECT,
        related_name='event_payment_methods'
    )
    instructions = models.TextField(
        blank=True,
        help_text="Instructions for using this payment method for the event."
        )
    
    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=['event', 'payment_method'],
                name='unique_event_payment_method'
            )
        ]

    def __str__(self):
        return f"{self.event.title} - {self.payment_method.name}"

class Payment(models.Model):

    PAYMENT_STATUS =[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    registration = models.ForeignKey(
        Registration,
        on_delete=models.CASCADE,
        related_name='payments'
    )

    event_payment_method = models.ForeignKey(
        EnabledPaymentMethod,
        on_delete=models.PROTECT,
        related_name='payments'
    )

    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    transaction_reference = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default='pending'
    )

    paid_at = models.DateTimeField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    gateway_reference = models.CharField(
    max_length=255,
    blank=True,
    null=True
    )

    # to return the a message from the payment gateway to the user after a payment is made
    gateway_response = models.TextField(
    blank=True
)

    @property
    def event(self):
        """
            Returns the event for this payment.
        """

        return self.registration.event
    
    @property
    def is_paid(self):
        """
        Returns True when payment has been completed.
        """

        return self.status == "completed"
    
    @property
    def is_refunded(self):
        return self.status == "refunded"
    
    def clean(self):
        """
        Ensure that the payment amount is non-negative and does not exceed the registration amount.
        """

        if self.amount_paid < 0:
            raise ValidationError("Amount paid cannot be negative.")

        if self.amount_paid > self.registration.registration_amount:
            raise ValidationError("Amount paid cannot exceed the registration amount.")
        

    def __str__(self):
       return f"{self.registration.name} - {self.amount_paid}"
    
class CheckIn(models.Model):
    """
    Represents an attendee's check-in for an event.
    """

    registration = models.ForeignKey(
        Registration,
        on_delete=models.CASCADE,
        related_name='checkins'
    )

    checked_in_at = models.DateTimeField(
        auto_now_add=True
    )

    checked_in_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='checkins',
        blank=True,
        null=True
    )
    attendance_date=models.DateField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['registration', 'attendance_date'],
                name = 'unique_daily_checkin'
            )
        ]
    
    def clean(self):
        """
        Ensure that the registration is eligible for check-in.
        """

        if not self.registration.can_check_in:
            raise ValidationError("This registration is not eligible for check-in.")
        
        if self.registration.event.attendance_mode == "single" and self.registration.checkins.exists():
            raise ValidationError("This registration has already checked in for this event.")
        
        if self.registration.event.attendance_mode == "daily":
            today = timezone.now().date()
            if self.registration.checkins.filter(attendance_date=today).exists():
                raise ValidationError("This registration has already checked in for today.")

    def __str__(self):
        return f"{self.registration.name} - {self.registration.event.title}"