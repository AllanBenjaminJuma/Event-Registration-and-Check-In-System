import secrets #cryptographically secure random generator

from datetime import timedelta # to clacu;ate  invitation expriy time

from django.utils import timezone # for timezone-aware dates

from .models import UserInvitation

def create_user_invitation(user, created_by=None):

    if user.is_active and user.email_verified:

        raise ValueError("User is already active.Cannot send invitation to an active user.")


    UserInvitation.objects.filter(
        user = user,
        used_at__isnull=True,
        revoked_at__isnull=True,
        ).update(revoked_at=timezone.now()) # revoke any existing invitations for the user:

#and the send a new invitation

    token = secrets.token_urlsafe(48)

    expires_at = timezone.now() + timedelta(hours=24)

    invitation = UserInvitation.objects.create(
        user=user,
        token=token,
        expires_at=expires_at,
        created_by=created_by,
    )
    return invitation