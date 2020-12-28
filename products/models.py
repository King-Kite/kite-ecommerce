import datetime
from autoslug import AutoSlugField
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.timezone import now
from .managers import ProductManager

User = get_user_model()

RATING_CHOICES = (
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
    )

class Type(models.Model):
    name = models.CharField(max_length=30, unique=True, help_text='Make sure the name is written in lower case.')
    slug = AutoSlugField(max_length=30, unique=True, populate_from='name', help_text='Unique value for type, created from name.')
    description = models.TextField(default='', blank=True, null=True)
    image = models.ImageField(default='', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=30, unique=True, help_text='Make sure the name is written in lower case.')
    slug = AutoSlugField(max_length=30, unique=True, populate_from='name', help_text='Unique value for category, created from name.')
    description = models.TextField(default='', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

class Color(models.Model):
    name = models.CharField(max_length=15, unique=True)
    slug = AutoSlugField(max_length=30, unique=True, populate_from='name', help_text='Unique value for category, created from name.')

    def __str__(self):
        return self.name

class Size(models.Model):
    value = models.CharField(max_length=20, unique=True)
    slug = AutoSlugField(max_length=30, unique=True, populate_from='value', help_text='Unique value for category, created from name.')

    def __str__(self):
        return self.value

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='categories')
    type = models.ForeignKey(Type, on_delete=models.CASCADE, related_name='types', blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True, help_text='Unique value for product page URL, created from type and category.')
    name = models.CharField(max_length=30)
    image = models.ImageField(default='', upload_to='product/images', blank=True, null=True)
    image1 = models.ImageField(upload_to='product/images', help_text='Additional images if needed', blank=True, null=True)
    image2 = models.ImageField(upload_to='product/images', help_text='Additional images if needed', blank=True, null=True)
    image3 = models.ImageField(upload_to='product/images', help_text='Additional images if needed', blank=True, null=True)
    color = models.ManyToManyField(Color, related_name='colors', blank=True)
    description = models.TextField(blank=True, null=True)
    parent_code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    new = models.BooleanField(default=True)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    objects = ProductManager()

    class Meta:
        verbose_name_plural = 'Products'
        unique_together = ['type', 'category']

    def __str__(self):
        return '%s %s' % (self.type, self.category)

    def get_absolute_url(self):
        return reverse('product-info', kwargs={
            'slug': self.slug
            })

    def change_new_product_status(self):
        future_date = datetime.timedelta(days=30)
        current_date = now()
        product_date = self.create_date
        if (current_date - product_date) > future_date:
            self.new = False
            return True
        return False

class ProductVariant(models.Model):
    parent = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants', blank=True, null=True)
    name = models.CharField(max_length=30, blank=True, null=True)
    size = models.ForeignKey(Size, on_delete=models.CASCADE, related_name='sizes', null=True)
    code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    gross_value = models.FloatField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['parent', 'size']

    def __str__(self):
        return '%s %s' % (self.parent, self.size)

    def get_absolute_url(self):
        return reverse('product-info', kwargs={
            'slug': self.parent.slug
            })

    def get_add_to_cart_url(self):
        return reverse('add-to-cart', kwargs={
            'slug': self.slug
            })

    def get_remove_from_cart_url(self):
        return reverse('remove-from-cart', kwargs={
            'id': self.id
            })

class Review(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_DEFAULT, related_name='reviews', default='Anonymous')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, related_name='reviews', blank=True, null=True)
    body = models.TextField()
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, default=5, blank=False, null=True)
    is_approved = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['author', 'product']

    def __str__(self):
        return '%s %s' % (self.author, self.product)

    def get_absolute_url(self):
        return reverse('product-info', kwargs={'slug': self.product.slug})
