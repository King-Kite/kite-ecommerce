from django.db import models


class AddressManager(models.Manager):
    def check_default_billing_address(self, user):
        billing_queryset = user.address.filter(user=user, address_type='B', default=True)
        if billing_queryset.exists():
            return billing_queryset
        else:
            return None

    def check_default_shipping_address(self, user):
        billing_queryset = user.address.filter(user=user, address_type='S', default=True)
        if billing_queryset.exists():
            return billing_queryset
        else:
            return None
