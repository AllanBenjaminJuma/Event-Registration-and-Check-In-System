from urllib import request

from django.utils import timezone

from django.shortcuts import render, get_object_or_404, redirect
from .models import Event, Registration, EventType, TicketType, PaymentMethod, EnabledPaymentMethod
from .forms import RegistrationForm

from django.db.models import Count

from django.contrib import messages

from django.db import IntegrityError, transaction

from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.cache import never_cache

from .forms import RegistrationForm
from .services import generate_registration_qr_code


# All views to create and manage events are in the dashboard app.

# display the dashboard page
# Display the dashboard page
@never_cache
@login_required
def dashboard(request):

    # Only retrieve events belonging to the logged-in user's organisation.
    events = Event.objects.filter(
        organisation=request.user.organisation
    )

    # Only show event types belonging to the logged-in user's organisation.
    event_types = EventType.objects.filter(
        organisation=request.user.organisation
    ).order_by('name')

    # Only count active events belonging to this organisation.
    active_events = events.filter(
        start_date__gte=timezone.now()
    ).order_by('start_date')

    total_events = events.count()

    total_active_events = active_events.count()

    # Count registrations belonging to this organisation's events.
    total_registrations = Registration.objects.filter(
        event__organisation=request.user.organisation
    ).count()

    # Count check-ins belonging to this organisation's events.
    total_checkins = Registration.objects.filter(
        event__organisation=request.user.organisation,
        checkins__isnull=False
    ).distinct().count()

    attendance_rate = 0

    if total_registrations > 0:
        attendance_rate = (
            total_checkins / total_registrations
        ) * 100

    no_shows = total_registrations - total_checkins

    return render(
        request,
        'admin/dashboard.html',
        {
            'total_events': total_events,
            'active_events': active_events,
            'total_active_events': total_active_events,
            'total_checkins': total_checkins,
            'total_registrations': total_registrations,
            'attendance_rate': attendance_rate,
            'no_shows': no_shows,
            'event_types': event_types
        }
    )


@never_cache
@login_required
@permission_required('events.view_eventtype', raise_exception=True)

def event_types(request):
    
    # Get only event types belonging to the logged-in user's organisation.
    event_types = EventType.objects.filter(organisation=request.user.organisation)

    event_types_count = event_types.count()

    event_types = EventType.objects.annotate(event_count=Count('events'))

    event_type_per_event= EventType.objects.annotate(event_count=Count('events'))

    most_used_event_type = EventType.objects.annotate(event_count=Count('events')).order_by('-event_count').first()

    total_events_count = Event.objects.filter(organisation=request.user.organisation).count()

    return render(request, 'events/event_types.html', {'event_types': event_types, 'event_type_per_event': event_type_per_event, 'event_types_count': event_types_count, 'total_events_count': total_events_count, 'most_used_event_type': most_used_event_type})

#create a new event type
@never_cache
@login_required
@permission_required('events.add_eventtype', raise_exception=True)
def create_event_type(request):

    if request.method == 'POST':

        name = request.POST.get('name')
        icon = request.POST.get('icon')
        description = request.POST.get('description')
        

        EventType.objects.create(
            name=name,
            icon=icon,
            description=description,
            organisation=request.user.organisation
        )

    return redirect('event_types') 

@never_cache
@login_required
@permission_required('events.change_eventtype', raise_exception=True)
def edit_event_type(request):

    if request.method == 'POST':

        event_type_id = request.POST.get('event_type_id')

        event_type = get_object_or_404(
            EventType,
            id=event_type_id,
            organisation=request.user.organisation #auto assign the user logged in the organisation who owns the event
        )

        event_type.name = request.POST.get('name')
        event_type.icon = request.POST.get('icon')
        event_type.description = request.POST.get('description')

        event_type.save()

        messages.success(
            request,
            f'Event type "{event_type.name}" updated successfully.'
        )

    return redirect('event_types')

@never_cache
@login_required
@permission_required('events.delete_eventtype', raise_exception=True)
def delete_event_type(request, id):

    event_type = get_object_or_404(EventType, id=id, organisation=request.user.organisation)

    event_count = event_type.events.count()

    if event_count > 0:
        messages.error(
            request,
            f'Cannot delete "{event_type.name}". It is currently used by {event_count} event(s).'
        )
        return redirect('event_types')

    event_type_name = event_type.name
    event_type.delete()

    messages.success(
        request,
        f'Event type "{event_type_name}" deleted successfully.'
    )

    return redirect('event_types')

#create a new event
@never_cache
@login_required
@permission_required('events.add_event', raise_exception=True)
def create_new_event(request):

    payment_methods = PaymentMethod.objects.filter(is_active=True)

    event_types = EventType.objects.filter(organisation=request.user.organisation).order_by('name')

    return render(request, 'events/create_event.html', {'event_types': EventType.objects.all(), 'payment_methods': payment_methods})

@never_cache
@login_required
@permission_required('events.add_event', raise_exception=True)
def create_event(request):

    # We only want this view to create an event when the browser
    # sends the form using HTTP POST.
    #
    # POST is appropriate here because we are creating data on
    # the server.
    if request.method != "POST":

        # If someone visits /create-event/ directly with a GET request,
        # send them back to the event creation page instead of trying
        # to create an empty event.
        return redirect("dashboard:create_new_event")


    try:

        # transaction.atomic() is Django's database transaction manager.
        #
        # Everything we do inside this block is treated as ONE
        # database transaction.
        #
        # If everything succeeds:
        #       → Django commits the changes.
        #
        # If something fails:
        #       → Django rolls the transaction back.
        #
        # This is important because creating an event involves several
        # related database operations:
        #
        #       Event
        #         ↓
        #       Tickets
        #         ↓
        #       Payment Methods
        #
        # We don't want the Event saved if saving its tickets fails.
        with transaction.atomic():


            # ==========================================================
            # EVENT TYPE
            # ==========================================================

            # request.POST.get("event_type") retrieves the value of the
            # <select name="event_type"> field from the submitted form.
            #
            # Example:
            #
            #     event_type = "3"
            #
            # We then use that ID to find the actual EventType object
            # from the database.
            event_type = get_object_or_404(
                EventType,
                pk=request.POST.get("event_type"),
                organisation=request.user.organisation
            )


            # ==========================================================
            # REGISTRATION TYPE
            # ==========================================================

            # Retrieve whether the organiser selected:
            #
            #     "free"
            # or
            #     "paid"
            #
            # The second argument, "free", is a default value.
            #
            # Therefore, if the browser doesn't send
            # registration_type at all, we don't get None.
            registration_type = request.POST.get(
                "registration_type",
                "free"
            )


            # ==========================================================
            # CREATE EVENT
            # ==========================================================

            # Event.objects.create() creates a new Event database row.
            #
            # Django takes the values below and generates the
            # corresponding SQL INSERT statement for us.
            event = Event.objects.create(


                # .get("title", "") retrieves the submitted title.
                #
                # The empty string is used as a fallback if the field
                # isn't submitted.
                #
                # .strip() removes unnecessary spaces from the beginning
                # and end of the user's input.
                title=request.POST.get(
                    "title",
                    ""
                ).strip(),


                # Get the event description and remove unnecessary
                # leading/trailing whitespace.
                description=request.POST.get(
                    "description",
                    ""
                ).strip(),


                # Associate this Event with the EventType object we
                # retrieved above.
                #
                # This creates the ForeignKey relationship:
                #
                #       Event → EventType
                event_type=event_type,


                # Our HTML calls this field "venue", but our database
                # model calls the field "location".
                #
                # Therefore we translate:
                #
                #       HTML:     venue
                #       Database: location
                location=request.POST.get(
                    "venue",
                    ""
                ).strip(),


                # Save the event's starting date/time.
                start_date=request.POST.get(
                    "start_date"
                ),


                # Save the event's ending date/time.
                end_date=request.POST.get(
                    "end_date"
                ),


                # Save when registration should open.
                registration_opens=request.POST.get(
                    "registration_opens"
                ),


                # Save when registration should close.
                registration_closes=request.POST.get(
                    "registration_closes"
                ),

                 # Automatically associate the event with the logged-in user's organisation.
                organisation=request.user.organisation,

                # request.POST values arrive as strings.
                #
                # Our Event.capacity field is a PositiveIntegerField,
                # so we convert the value into an integer before saving.
                #
                # The "or 0" means that if the field is empty,
                # we use 0 instead.
                capacity=int(
                    request.POST.get("capacity") or 0
                ),


                # Save whether this is a free or paid event.
                registration_type=registration_type,
            )


            # ==========================================================
            # TICKETS
            # ==========================================================

            # getlist() is important here.
            #
            # A normal .get() retrieves ONE value.
            #
            # But our wizard can have multiple tickets:
            #
            #     VIP
            #     Regular
            #     Student
            #
            # Therefore getlist() retrieves ALL values submitted using
            # the same field name.
            ticket_names = request.POST.getlist(
                "ticket_name[]"
            )

            ticket_prices = request.POST.getlist(
                "ticket_price[]"
            )

            ticket_capacities = request.POST.getlist(
                "ticket_capacity[]"
            )

            ticket_descriptions = request.POST.getlist(
                "ticket_description[]"
            )


            # enumerate() allows us to loop through the ticket names
            # while getting BOTH:
            #
            #     index → position in the list
            #     name  → actual ticket name
            #
            # Example:
            #
            #     ticket_names = ["VIP", "Regular"]
            #
            # enumerate() gives:
            #
            #     index=0, name="VIP"
            #     index=1, name="Regular"
            #
            # The index lets us retrieve the corresponding price,
            # capacity and description from the other lists.
            for index, name in enumerate(ticket_names):


                # Remove unnecessary spaces from the ticket name.
                #
                # Example:
                #
                #     "   VIP   "
                #
                # becomes:
                #
                #     "VIP"
                name = name.strip()


                # If a ticket name is empty, don't create a useless
                # TicketType database record.
                if not name:
                    continue


                # Retrieve the price at the SAME position as the
                # current ticket.
                #
                # Example:
                #
                #     index = 0
                #     name = "VIP"
                #
                # ticket_prices[0] gives the VIP price.
                #
                # The conditional expression prevents an IndexError
                # if the submitted lists don't have the same length.
                price = (
                    ticket_prices[index]
                    if index < len(ticket_prices)
                    else 0
                )


                # Retrieve the capacity belonging to this ticket.
                quantity = (
                    ticket_capacities[index]
                    if index < len(ticket_capacities)
                    else 0
                )


                # Retrieve the description belonging to this ticket.
                description = (
                    ticket_descriptions[index]
                    if index < len(ticket_descriptions)
                    else ""
                )


                # ------------------------------------------------------
                # FREE EVENT PROTECTION
                # ------------------------------------------------------

                # Frontend JavaScript is useful for giving the user
                # immediate feedback.
                #
                # BUT JavaScript is NOT a security boundary.
                #
                # A user can disable JavaScript or send a custom POST
                # request directly to our Django server.
                #
                # Therefore the backend must enforce the rule again:
                #
                #       FREE EVENT → PRICE MUST BE 0
                #
                if registration_type == "free":

                    price = 0


                # ------------------------------------------------------
                # CREATE TICKET
                # ------------------------------------------------------

                # Create the TicketType database record.
                #
                # The event=event line establishes the ForeignKey:
                #
                #       Event
                #          ↓
                #       TicketType
                #
                # So this ticket belongs specifically to the event
                # we just created above.
                TicketType.objects.create(

                    event=event,

                    name=name,

                    description=description.strip(),

                    # amount stores the ticket price.
                    amount=price or 0,

                    # quantity stores how many tickets are available.
                    quantity=int(quantity or 0),
                )


            # ==========================================================
            # PAYMENT METHODS
            # ==========================================================

            # Free events don't need payment methods.
            #
            # Therefore we only process payment methods when the
            # organiser selected "Paid Event".
            if registration_type == "paid":


                # getlist() retrieves ALL selected payment methods.
                #
                # For example:
                #
                #     ["mpesa", "airtel", "card"]
                #
                # rather than only retrieving one checkbox.
                payment_method_ids = request.POST.getlist(
                    "payment_methods[]"
                )


                # Process every selected payment method.
                for method_id in payment_method_ids:


                    # Find the corresponding payment method that
                    # already exists in our PaymentMethod table.
                    #
                    # We don't create a new PaymentMethod here.
                    #
                    # PaymentMethod is our MASTER list.
                    #
                    # Example:
                    #
                    #     PaymentMethod
                    #     ----------------
                    #     M-Pesa
                    #     Airtel Money
                    #     Visa
                    #
                    # We simply find the existing record.
                    payment_method = PaymentMethod.objects.get(
                        pk=method_id,
                        is_active=True
                    )


                    # EnabledPaymentMethod creates the relationship
                    # between THIS event and the selected payment
                    # method.
                    #
                    # Conceptually:
                    #
                    #     Event
                    #       │
                    #       ├── M-Pesa
                    #       ├── Airtel Money
                    #       └── Visa
                    #
                    EnabledPaymentMethod.objects.create(

                        event=event,

                        payment_method=payment_method
                    )


        # We are now OUTSIDE transaction.atomic().
        #
        # That means the transaction has successfully completed and
        # Django has committed the Event, Tickets and Payment Methods
        # to the database.
        #
        # Now it is safe to tell the user that the event was created.
        messages.success(
            request,
            f'"{event.title}" created successfully.'
        )


        # Redirect after a successful POST.
        #
        # This is part of the Post/Redirect/Get pattern:
        #
        #     POST → save data → REDIRECT → GET
        #
        # It prevents the browser from accidentally submitting the
        # event again if the user refreshes the page.
        return redirect(
            "dashboard"
        )


    except Exception as e:


        # If an exception occurs anywhere inside transaction.atomic(),
        # Django rolls the transaction back.
        #
        # Therefore we don't end up with:
        #
        #     Event saved ✓
        #     Ticket saved ✓
        #     Payment method failed ✗
        #
        # Instead, the database returns to its previous state.
        messages.error(
            request,
            f"Error creating event: {str(e)}"
        )


        # Return the user to the creation page so they can correct
        # the problem and try again.
        return redirect(
            "dashboard:create_new_event"
        )                    



# Fetch all events that are upcoming
def event_list(request):

    events = Event.objects.filter(start_date__gte=timezone.now()).order_by('start_date')

   
    

    return render(request, 'events/event_list.html', {'events': events, 'now': timezone.now(),})

# fetch all events that are in the past.
def past_events(request):
    events = Event.objects.filter(start_date__lt=timezone.now()).order_by('-start_date')

    return render(request, 'events/past_events.html', {'events': events, 'now': timezone.now()})

# view event details and handle registration

def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    form = RegistrationForm()

    if request.method == 'POST':

        form = RegistrationForm(request.POST, instance=Registration(event=event))

        if form.is_valid():

            try:
                registration = form.save(commit=False)

                # generate the QR code using th registration's token

                generate_registration_qr_code(registration)
                                #

                return render(request, 'events/registration_success.html', { 'event': event,
                    'registration': registration
                })

            except IntegrityError:
                # Duplicate email or phone caught here
                form.add_error(None, "You have already registered for this event using this email or phone.")
    
    event_registrations = Registration.objects.filter(event=event).count()

    return render(request, 'events/event_detail.html', {
        'event': event,
        'form': form,
        'event_registrations': event_registrations
    })

def checkin(request, event_uuid):

    event = get_object_or_404(
        Event,
        uuid=event_uuid
    )

    message = None
    success = False

    if request.method == "POST":

        identifier = request.POST.get("identifier", "").strip()

        # Find registration (email OR phone)
        registration = Registration.objects.filter(
            event=event,
            email=identifier
        ).first()

        if not registration:
            registration = Registration.objects.filter(
                event=event,
                phone=identifier
            ).first()

        #  Not found
        if not registration:
            message = "Registration not found for this event."

            return render(request, 'events/checkin.html', { 'event': event, 'message': message, 'success': success })


        else:

            # SAFE TRANSACTION (prevents double check-in bugs)
            with transaction.atomic():

                registration = Registration.objects.select_for_update().get(
                    id=registration.id
                )

                #  Already checked in
                if registration.checkins:

                    message = (
                        f"Already checked in at "
                        f"{registration.checked_in_at.strftime('%Y-%m-%d %H:%M:%S')}"
                    )

                else:

                    # Mark check-in
                    registration.checkedin = True
                    registration.checked_in_at = timezone.now()
                    registration.save()

                    success = True

                    message = (
                        f"Welcome {registration.name}! "
                        "Check-in successful."
                    )

    return render(
        request,
        "events/checkin.html",
        {
            "event": event,
            "message": message,
            "success": success
        }
    )