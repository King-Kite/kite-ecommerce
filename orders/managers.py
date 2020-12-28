from django.db import models

class CartItemManager(models.Manager):
    def get_by_natural_key(self, user, product):
        return self.get(user=user, product=product)

    def get_item_quantity_count(self, user):
        if user.is_authenticated:
            count = 0
            queryset = user.useritems.filter(user=user, ordered=False)
            if queryset.exists():
                for obj in queryset:
                    count += obj.quantity
                return count
        return 0

    def get_original_price(self, user):
        sum = 0
        queryset = user.useritems.filter(user=user, ordered=False)
        if queryset.exists():
            for obj in queryset:
                sum += obj.product.price * obj.quantity
            return sum
        return 0

    def get_final_price(self, user):
        sum = 0
        queryset = user.useritems.filter(user=user, ordered=False)
        if queryset.exists():
            for obj in queryset:
                if obj.get_total_discount_product_price():
                    sum += obj.get_total_discount_product_price()
                else:
                    sum += obj.get_total_product_price()
            return sum
        return 0

    def get_total_discount(self, user):
        total_discount = self.get_original_price(user) - self.get_final_price(user)
        return total_discount

