from django.db import models
from django.contrib.auth import get_user_model
from django_countries.fields import CountryField
from make_payments.models import Payments
from products.models import ProductVariant
from users.models import Address
from .managers import CartItemManager

User = get_user_model()

ORDER_STATUS = (
    ('P', 'Processing'),
    ('BD', 'Being Delivered'),
    ('D', 'Delivered'),
    ('RR', 'Refund Requested'),
    ('RG', 'Refund Granted')
)

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='useritems')
    product = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.IntegerField(default=1)
    date_added = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    ordered = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = CartItemManager()

    def __str__(self):
        return f"{self.quantity}    of    {self.product}   by    {self.user}"

    def get_total_product_price(self):
        return self.quantity * self.product.price

    def get_total_discount_product_price(self):
        return self.quantity * self.product.discount_price


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payments, on_delete=models.CASCADE, blank=True, null=True)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    products = models.ManyToManyField(CartItem, related_name='cartitem')
    billing_address = models.ForeignKey(Address, related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
    shipping_address = models.ForeignKey(Address, related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(auto_now=True)
    ordered = models.BooleanField(default=False)
    status = models.CharField(max_length=3, default='P', choices=ORDER_STATUS)

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = CartItem.objects.get_final_price(self.user)
        return total


class OrderProductInstance(models.Model):
    user = models.ForeignKey(User, related_name='user_orders', on_delete=models.CASCADE, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True)
    product_name = models.CharField(max_length=100, blank=True, null=True)
    product_image = models.ImageField(default='', upload_to='order_product_instance/images', blank=True, null=True)
    product_price = models.FloatField(blank=True, null=True)
    product_size = models.CharField(max_length=20, blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    ordered = models.BooleanField(default=False)
    status = models.CharField(max_length=3, default='P', choices=ORDER_STATUS)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s %s' % (self.order, self.product_name)


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"
