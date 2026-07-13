from django.urls import path
from . import views

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('past-events/', views.past_events, name='past_events'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('check-in/<uuid:event_uuid>/', views.checkin, name='checkin'),

    path('dashboard', views.dashboard, name='dashboard'),
    path('dashboard/events/create/', views.create_event, name='create_event'),

    path('dashboard/event-types/', views.event_types, name='event_types'),
    path('dashboard/event-types/create/', views.create_event_type, name='create_event_type'),
    path('dashboard/event-types/edit/', views.edit_event_type,  name='edit_event_type')


    #path('check-in/success/<uuid:token>/', views.check_in_success, name='check_in_success'),
]