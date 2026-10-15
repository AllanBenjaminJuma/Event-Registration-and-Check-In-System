from django.urls import path

from . import views


urlpatterns = [

    # List all organisations on the platform.
    path("", views.organisation_list, name="organisation_list"),

    # Create a new organisation.
    path("create/", views.create_organisation,name="organisation_create",),
]