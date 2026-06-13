from django.urls import path
from . import views

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('past-events/', views.past_events, name='past_events'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('check-in/<uuid:event_uuid>/', views.checkin, name='checkin'),
    #path('check-in/success/<uuid:token>/', views.check_in_success, name='check_in_success'),
]