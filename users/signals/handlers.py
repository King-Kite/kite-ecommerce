from django.conf import settings
from django.contrib.auth import get_user_model, user_logged_in, user_logged_out
from django.core.mail import BadHeaderError, send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpResponse
from users.models import ContactUs, Profile, LoggedInUser

User = get_user_model()

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(user_logged_in)
def on_user_logged_in(sender, request, **kwargs):
    LoggedInUser.objects.get_or_create(user=kwargs.get('user'))


@receiver(user_logged_out)
def on_user_logged_out(sender, request, **kwargs):
    LoggedInUser.objects.filter(user=kwargs.get('user')).delete()


@receiver(post_save, sender=ContactUs)
def send_email_message(sender, instance, created, **kwargs):
    if created:
        try:
            send_mail(
                instance.subject,
                instance.message,
                instance.email,
                [settings.EMAIL_HOST_USER],
                fail_silently=False,
                )
        except BadHeaderError:
            return HttpResponse('Invalid header found.')

