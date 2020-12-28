from django import template
from wishlists.models import Wishlist

register = template.Library()

@register.filter
def wishlist_item_count(user):
    if user.is_authenticated:
        queryset = Wishlist.objects.filter(user=user)
        if queryset.exists():
            return queryset.count()
    return 0

