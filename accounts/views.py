from django.shortcuts import render, get_object_or_404
from django.contrib import messages #to provide user feedback messages
from django.contrib.auth.password_validation import validate_password # to validate password using django's validators
from django.core.exceptions import ValidationError # to catch validation errors
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone # to get the current time

from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

from accounts.models import UserInvitation 

from django.contrib.auth import login
from .forms import LoginForm
# Create your views here.

def login_view(request):

    if request.user.is_authenticated:
        return redirect('accounts:login_success')

    form = LoginForm()

    if request.method =='POST':

        form = LoginForm(request.POST)

        if form.is_valid():

            user = form.user

            login(request, user) # create the session for the already authenticated user fro authenticate(...)

            return redirect('accounts:login_success')
    return render(request, 'accounts/login.html', {'form':form})

@never_cache
@login_required
def login_success(request):

    return render(request, 'accounts/login_success.html')


def activate_account(request,token):

    invitation = get_object_or_404(UserInvitation, token=token)

    
    if invitation.is_used:

        messages.error(request, "This invitation has already been used.")
        return render(request, 'accounts/activation_failed.html')
    
    if invitation.revoked_at is not None:

        messages.error(request, "This invitation has been revoked.")
        return render(request, 'accounts/activation_failed.html')
    if invitation.is_expired:

        messages.error(request, "This invitation has expired.")
        return render(request, 'accounts/activation_failed.html')

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not password or not confirm_password:
            messages.error(request,'Please provide a password and confirm it.')

        elif password != confirm_password:
            messages.error(request, 'The passwords must match!')

        else:
            try:
                
                validate_password(password, user=invitation.user)

            except ValidationError as error:
                for message in error.messages:
                    messages.error(request, message,)

            else:

                user = invitation.user

                user.set_password(password)

                user.is_active = True
                user.email_verified = True

                user.save(update_fields=['password','is_active','email_verified'])


                invitation.used_at = timezone.now()
                invitation.save(update_fields=['used_at'])

                messages.success(request, 'Your account has been succesfully activated. You can now log in.',)

                return redirect('accounts:login')
            

    
    return render(request, 'accounts/activate_account.html', {'invitation': invitation})