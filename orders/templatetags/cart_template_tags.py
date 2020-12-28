from django import template
from orders.models import CartItem

register = template.Library()

@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        queryset = CartItem.objects.filter(user=user, ordered=False)
        if queryset.exists():
            return queryset.count()
    return 0

@register.filter
def cart_item_quantity_count(user):
    if user.is_authenticated:
        lists = []
        queryset = CartItem.objects.filter(user=user, ordered=False)
        if queryset.exists():
            for obj in queryset:
                lists.append(obj.quantity)
            return sum(lists)
    return 0

