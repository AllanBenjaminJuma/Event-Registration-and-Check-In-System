from django.utils import timezone

from django.shortcuts import render, get_object_or_404, redirect
from .models import Event, Registration, EventType
from .forms import RegistrationForm

from django.db.models import Count

from django.contrib import messages


from django.db import IntegrityError, transaction

# All views to create and manage events are in the dashboard app.

# display the dashboard page
def dashboard(request):

    events = Event.objects.all()

    event_types = EventType.objects.all().order_by('name') # to list the event types when crating a new event

    total_events = events.count()

    active_events = Event.objects.filter(start_date__gte=timezone.now()).order_by('start_date')

    total_active_events = active_events.count()

    total_checkins = Registration.objects.filter(is_checked_in=True).count()

    total_registrations = Registration.objects.count()

    attendance_rate = 0

    if total_registrations > 0:
        attendance_rate = (total_checkins / total_registrations) * 100
    
    no_shows = total_registrations - total_checkins




    return render(request, 'admin/dashboard.html',{'total_events': total_events, 'active_events': active_events, 'total_active_events': total_active_events, 'total_checkins': total_checkins, 'total_registrations': total_registrations, 'attendance_rate': attendance_rate, 'no_shows': no_shows, 'event_types': event_types})

def event_types(request):
    
    event_types = EventType.objects.all()

    event_types_count = event_types.count()

    event_types = EventType.objects.annotate(event_count=Count('events'))

    event_type_per_event= EventType.objects.annotate(event_count=Count('events'))

    most_used_event_type = EventType.objects.annotate(event_count=Count('events')).order_by('-event_count').first()

    total_events_count = Event.objects.count()

    return render(request, 'events/event_types.html', {'event_types': event_types, 'event_type_per_event': event_type_per_event, 'event_types_count': event_types_count, 'total_events_count': total_events_count, 'most_used_event_type': most_used_event_type})

#create a new event type
def create_event_type(request):

    if request.method == 'POST':

        name = request.POST.get('name')
        icon = request.POST.get('icon')
        description = request.POST.get('description')

        EventType.objects.create(
            name=name,
            icon=icon,
            description=description
        )

    return redirect('event_types') 

def edit_event_type(request):

    if request.method == 'POST':

        event_type_id = request.POST.get('event_type_id')

        event_type = get_object_or_404(
            EventType,
            id=event_type_id
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

def delete_event_type(request, id):

    event_type = get_object_or_404(EventType, id=id)

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
from django.shortcuts import redirect, get_object_or_404
from .models import Event, EventType


def create_event(request):

    if request.method == 'POST':

        title = request.POST.get('title')
        description = request.POST.get('description')
        location = request.POST.get('location')
        start_date = request.POST.get('date')  
        capacity = request.POST.get('capacity')
        free_or_paid = request.POST.get('free_or_paid')

        event_type_id = request.POST.get('event_type')

        event_type = get_object_or_404(
            EventType,
            id=event_type_id
        )

        Event.objects.create(
            title=title,
            description=description,
            location=location,
            start_date=start_date,
            event_type=event_type,
            free_or_paid=free_or_paid,
            capacity=capacity
        )

    return redirect('dashboard')  # Redirect to the same page after creating the event
    


# Fetch all events that are upcoming.
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