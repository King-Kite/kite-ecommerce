from django.db import models
from django.conf import settings

from payments.models import BasePayment
from products.models import Product, ProductVariant


class Payments(BasePayment):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)

    def get_failure_url(self):
        return '/checkout'

    def get_success_url(self):
        return '/'

    def __str__(self):
        return self.user.username

