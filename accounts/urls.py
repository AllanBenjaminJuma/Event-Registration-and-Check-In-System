from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views

from . import views

app_name = 'accounts'

urlpatterns = [

    path(
        'activate/<str:token>/',
        views.activate_account,
        name='activate_account',
    ),

    path(
        'login/',
        views.login_view,
        name='login',
    ),

    path('success', views.login_success, name='login_success'),

    path('logout/',auth_views.LogoutView.as_view(next_page="accounts:login",), name="logout",),

    # Password reset - request
    path(
    'password-reset/',
    auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset.html',
        email_template_name='accounts/password_reset_email.txt',
        html_email_template_name='accounts/password_reset_email.html',
        subject_template_name='accounts/password_reset_subject.txt',
        success_url=reverse_lazy(
            'accounts:password_reset_done'
        ),
    ),
    name='password_reset',
),

    # Password reset - email sent
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='accounts/password_reset_done.html',
        ),
        name='password_reset_done',
    ),

    # Password reset - create new password
    path(
        'password-reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html',
            success_url=reverse_lazy(
                'accounts:password_reset_complete'
            ),
        ),
        name='password_reset_confirm',
    ),

    # Password reset - complete
    path(
        'password-reset/complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='accounts/password_reset_complete.html',
        ),
        name='password_reset_complete',
    ),
]