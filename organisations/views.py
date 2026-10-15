from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect

import secrets
from datetime import timedelta

from django.contrib import messages
from django.db import transaction
from django.utils import timezone

from accounts.models import User, UserInvitation

from django.db.models import Count
from accounts.models import User


from .models import Organisation
# Create your views here.

def platform_admin_required(view_func):

    @login_required
    def wrapper(request, *args, **kwargs):

        if request.user.organisation is not None:
            return redirect("dashboard")  # Redirect to dashboard if the user is not a platform admin

        if not request.user.groups.filter(name="Platform Administrator").exists():
            return redirect("dashboard")
        return view_func(request, *args, **kwargs)
    return wrapper

@never_cache
@platform_admin_required
def organisation_list(request):

    organisations=Organisation.objects.all().order_by('name')

    organisations_count = organisations.count()

    active_organisations_count = organisations.filter(is_active=True).count()

    total_admins_count = User.objects.filter(
    groups__name__in=[
        "Platform Administrator",
        "Organisation Administrator",
    ]
).distinct().count()
    
    return render(request, "organisations/organisations.html", {"organisations": organisations, "organisations_count": organisations_count, "active_organisations_count": active_organisations_count, "total_admins_count": total_admins_count})


@never_cache
@platform_admin_required
def create_organisation(request):

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        code = request.POST.get("code", "").strip()
        email = request.POST.get("email", "").strip()
        address = request.POST.get("address", "").strip()
        

        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        admin_email = request.POST.get("admin_email", "").strip()
        phone = request.POST.get("phone", "").strip()

        if not all([name, code, email, first_name, last_name, admin_email, phone]):
            messages.error(request, 'Please fill in all the details')
            return redirect("organisation_create")

        if Organisation.objects.filter(code__iexact=code).exists():
            messages.error(request, 'Organisation code already in use.')
            return redirect("organisation_create")

        if User.objects.filter(email__iexact=admin_email).exists():
            messages.error(request, 'Admin email already in use.')
            return redirect("organisation_create")

        admin_group = Group.objects.filter(name="Organisation Administrator").first()

        if admin_group is None:
            messages.error(request, 'Organisation Admin role not configured. Contact platform administrator.')
            return redirect("organisation_create")

        try:
            with transaction.atomic():
                organisation = Organisation.objects.create(
                    name=name,
                    code=code,
                    email=email or None,
                    address=address or None,
                    
                )

                admin_user = User.objects.create_user(
                    email=admin_email,
                    password = None,
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone or None,
                    organisation=organisation,
                    is_active=False,
                    email_verified=False
                )
                
                admin_user.groups.add(admin_group)

                UserInvitation.objects.create(
                    user=admin_user,
                    token=secrets.token_urlsafe(48),
                    expires_at=timezone.now() + timedelta(days=2),
                    created_by=request.user)          

        except Exception as e:
            print("Error creating organisation and admin user:", repr(e))
            messages.error(
                request,
                "The organisation could not be created. Please check the details and try again."
            )
            return redirect("organisation_list")

        messages.success(
            request,
            "Organisation and its first administrator were created successfully. "
            "An invitation has been recorded."
        )

        return redirect("organisation_list")

    return redirect("organisation_list")
