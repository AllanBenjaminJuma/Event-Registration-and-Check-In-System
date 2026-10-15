from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

class Command(BaseCommand):

    # create the initial platform admin account - outside all organisations and responsible for managing the events platform

    help = "Creates the initial platform admin account"

    def handle(self, *args, **options):

        User = get_user_model()

        email = input("Platform Admin email: ").strip()
        first_name = input("First name: ").strip()
        last_name = input("Last name: ").strip()

        from getpass import getpass #to securely getting the password without displaying it

        password = getpass("Password: ")

        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.ERROR("A user with this email already exists.")
            )
            return
        try:
            platform_admin_group = Group.objects.get(
                name="Platform Administrator"
            )
        except Group.DoesNotExist:
            self.stdout.write(
                self.style.ERROR("Platform Administrator role does not exist." "Run 'python manage.py create_roles' first")
            )
            return
        user = User.objects.create_user(
            email=email,
            password=password, first_name=first_name, last_name=last_name, organisation=None,is_active=True, email_verified=True)

        user.groups.add(platform_admin_group)

        self.stdout.write(
            self.style.SUCCESS(f"Platform admin account created successfully for {user.email}.")
        )