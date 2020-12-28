from django.db import models
from django.contrib.auth.models import AbstractUser
from django_countries.fields import CountryField
from django.utils.translation import gettext_lazy as _
from .managers import AddressManager

ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
    )

SEX_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
    )

class CustomUser(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)


class ContactUs(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    subject = models.CharField(max_length=100)
    message = models.TextField()
    read = models.BooleanField(default=False)
    replied = models.BooleanField(default=False)
    create_date = models.DateTimeField(auto_now_add=True)
    replied_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Contact Us'

    def __str__(self):
        return '%s %s' % (self.name, self.email)


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    image = models.ImageField(default='profile_images/default.png',upload_to='profile_images', blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    sex = models.CharField(choices=SEX_CHOICES, max_length=1, default='N', blank=False, null=True)
    country = CountryField(blank_label='(select country)', default='NG')
    state = models.CharField(max_length=20)
    city = models.CharField(max_length=20)
    address = models.TextField(blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f'{self.user} Profile'


class LoggedInUser(models.Model):
    user = models.OneToOneField(CustomUser, related_name='logged_in_user', on_delete=models.CASCADE)
    session_key = models.CharField(max_length=32, null=True, blank=True)

    def __str__(self):
        return self.user.username

class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='address')
    address1 = models.CharField(max_length=100)
    address2 = models.CharField(max_length=100)
    country = CountryField(multiple=False, default='NG')
    state = models.CharField(max_length=20)
    city = models.CharField(max_length=20)
    zipcode = models.CharField(max_length=50)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    objects = AddressManager()

    class Meta:
        verbose_name_plural= "Addresses"

    def __str__(self):
        return self.user.username
