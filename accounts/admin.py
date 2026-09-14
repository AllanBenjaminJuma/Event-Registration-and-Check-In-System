from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    model = User

    # Controls the columns displayed in the user list.
    list_display = (
        'email',
        'first_name',
        'last_name',
        'organisation',
        'is_active',
        'email_verified',
        'is_staff',
    )

    # Adds filters on the right side of the user list.
    list_filter = (
        'is_active',
        'email_verified',
        'is_staff',
        'is_superuser',
        'groups',
    )

    # Sort users alphabetically by email.
    ordering = ('email',)

    # Defines which fields the admin can search.
    search_fields = (
        'email',
        'first_name',
        'last_name',
        'phone',
        'organisation__name',  # Allows searching by organisation name
    )

    # Defines how an existing user is displayed/edited.
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'email',
                    'password',
                )
            },
        ),

        (
            'Personal Information',
            {
                'fields': (
                    'first_name',
                    'last_name',
                    'phone',
                )
            },
        ),

        (
            'Organisation',
            {
                'fields': (
                    'organisation',
                )
            },
        ),

        (
            'Account Status',
            {
                'fields': (
                    'is_active',
                    'email_verified',
                    'is_staff',
                )
            },
        ),

        (
            'Roles & Permissions',
            {
                'fields': (
                    'is_superuser',
                    'groups',
                    'user_permissions',
                )
            },
        ),

            )

    # Defines the fields displayed when an administrator creates a user.
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'email',
                    'first_name',
                    'last_name',
                    'phone',
                    'password1',
                    'password2',
                ),
            },
        ),
    )