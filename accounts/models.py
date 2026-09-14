from django.db import models
#We use abstractBaseUser to create a customer aithentication we want instead of the username
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin 
from django.utils import timezone

from organisations.models import Organisation

# Create your models here.

class UserManager(BaseUserManager):


    def create_user(self, email, password=None, **extra_fields):

        if not email:
            raise ValueError('The Email field is required')
        email = self.normalize_email(email)

        user  =self.model(email=email, **extra_fields)

        if password:
            user.set_password(password) #Hash the poassword securely

        else:
            user.set_unusable_password() # prevent login until ccount is activated

        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('email_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email=email, password=password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(unique=True)

    first_name = models.CharField(max_length=100)

    last_name = models.CharField(max_length=100)

    phone = models.CharField(max_length=20, blank=True, null=True)

    is_active= models.BooleanField(default=False) # define new users are inactive vy default  until they activate accounts

    email_verified = models.BooleanField(default=False) # email by defaukt is not verified until user verifies

    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    objects  = UserManager()

    organisation = models.ForeignKey(Organisation, on_delete=models.PROTECT,related_name='users') # allow users to be associated with an organisation

    USERNAME_FIELD = 'email' # email will be used as the log in identity

    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email


class UserInvitation(models.Model):

    user= models.ForeignKey(User, on_delete=models.CASCADE, related_name='invitations',)

    token = models.CharField(max_length=128, unique=True,)

    expires_at = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    used_at = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_invitations',)

    revoked_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):

        return f"invitation for {self.user.email}"

    @property
    def is_used(self):
        return self.used_at is not None # check whether the invitation has been used or not


    @property
    def is_revoked(self):
        return self.revoked_at is not None # check whether the invitation has been revoked or not
    
    @property
    def is_expired(self):

        return timezone.now() >=self.expires_at #check wther link has expeired