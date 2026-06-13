from django.utils import timezone

from django.shortcuts import render, get_object_or_404, redirect
from .models import Event, Registration
from .forms import RegistrationForm


from django.db import IntegrityError, transaction


# Fetch all events that are upcoming.
def event_list(request):

    events = Event.objects.filter(date__gte=timezone.now()).order_by('date')

    return render(request, 'events/event_list.html', {'events': events, 'now': timezone.now()})

# fetch all events that are in the past.
def past_events(request):
    events = Event.objects.filter(date__lt=timezone.now()).order_by('-date')

    return render(request, 'events/past_events.html', {'events': events, 'now': timezone.now()})

# view event details and handle registration

def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    form = RegistrationForm()

    if request.method == 'POST':

        form = RegistrationForm(request.POST)

        if form.is_valid():

            try:
                registration = form.save(commit=False)
                registration.event = event
                registration.save()

                return render(request, 'events/registration_success.html', { 'event': event,
                    'registration': registration
                })

            except IntegrityError:
                # Duplicate email or phone caught here
                form.add_error(None, "You have already registered for this event using this email or phone.")

    return render(request, 'events/event_detail.html', {
        'event': event,
        'form': form
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
                if registration.is_checked_in:

                    message = (
                        f"Already checked in at "
                        f"{registration.checked_in_at.strftime('%Y-%m-%d %H:%M:%S')}"
                    )

                else:

                    # Mark check-in
                    registration.is_checked_in = True
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