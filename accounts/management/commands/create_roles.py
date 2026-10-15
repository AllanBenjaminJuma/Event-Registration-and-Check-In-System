from django.core.management.base import BaseCommand  # Base class for custom Django commands
from django.contrib.auth.models import Group, Permission  # Django's roles and permissions


class Command(BaseCommand):
    """
    Creates the roles used by the Events Management System
    and assigns the appropriate permissions to each role.
    """

    help = "Creates and configures System roles"

    def handle(self, *args, **options):

        # Define the roles and the permissions each role should receive
        roles = {

            "Platform Administrator":{
                "permissions": [],
            },

            "Organisation Administrator":{
                "permissions": "organisation_all",
            },

            "System Administrator": {
                "permissions": "events_all",
            },

            "Event Manager": {
                "permissions": [
                    "add_event",
                    "change_event",
                    "view_event",
                    "view_eventtype",
                    "add_tickettype",
                    "change_tickettype",
                    "view_tickettype",
                    "view_registration",
                ],
            },

            "Registration Officer": {
                "permissions": [
                    "add_registration",
                    "change_registration",
                    "view_registration",
                    "view_event",
                    "view_tickettype",
                ],
            },

            "Check-In Officer": {
                "permissions": [
                    "add_checkin",
                    "view_checkin",
                    "view_registration",
                    "view_event",
                ],
            },

            "Finance Officer": {
                "permissions": [
                    "view_payment",
                    "change_payment",
                    "view_paymentmethod",
                    "view_enabledpaymentmethod",
                    "view_registration",
                ],
            },

            "Event Configuration Officer": {
                "permissions": [
                    "add_eventtype",
                    "change_eventtype",
                    "view_eventtype",

                    "add_tickettype",
                    "change_tickettype",
                    "view_tickettype",

                    "add_paymentmethod",
                    "change_paymentmethod",
                    "view_paymentmethod",

                    "add_enabledpaymentmethod",
                    "change_enabledpaymentmethod",
                    "view_enabledpaymentmethod",
                ],
            },
        }

        # Process each role defined above
        for role_name, role_data in roles.items():

            # Get the role if it exists, otherwise create it
            group, created = Group.objects.get_or_create(
                name=role_name
            )

            if created:

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created role: {role_name}"
                    )
                )

            else:

                self.stdout.write(
                    f"Role already exists: {role_name}"
                )

            # System Administrator receives every Events permission
            if role_data["permissions"] == "organisation_all":

                permissions = Permission.objects.filter(
                    content_type__app_label__in=["events", "accounts"]
                )

            elif role_data["permissions"] =="events_all":

                permissions = Permission.objects.filter(
                    content_type__app_label="events"
                )

            else:

                # Get only the permissions assigned to this particular role
                permissions = Permission.objects.filter(
                    content_type__app_label__in="events",
                    codename__in=role_data["permissions"],
                )

            # Assign the permissions to the role
            group.permissions.set(permissions)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Permissions configured for: {role_name}"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                "All Events Management System roles configured successfully."
            )
        )