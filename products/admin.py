from django.contrib import admin
from django.contrib import messages
from django.utils.translation import ngettext
from .models import Type, Category, Color, Product, ProductVariant, Review, Size


class ProductVariantInline(admin.StackedInline):
    model = ProductVariant
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ['type', 'category', 'featured', 'new' , 'update_date', 'create_date']

    list_filter = ['type', 'category', 'featured', 'new' , 'update_date', 'create_date']

    inlines = [ProductVariantInline,]

    actions = ['mark_featured', 'mark_not_featured', 'mark_new', 'mark_old']

    def mark_featured(self, request, queryset):
        updated = queryset.update(featured=True)
        self.message_user(request, ngettext(
            '%d product was successfully marked as Featured.',
            '%d products were successfully marked as Featured.',
            updated,
            ) % updated, messages.SUCCESS)
    mark_featured.allowed_permissions = ('change',)
    mark_featured.short_description = "Mark selected orders as Featured"

    def mark_not_featured(self, request, queryset):
        updated = queryset.update(featured=False)
        self.message_user(request, ngettext(
            '%d product was successfully marked as not Featured.',
            '%d products were successfully marked as not Featured.',
            updated,
            ) % updated, messages.SUCCESS)
    mark_not_featured.allowed_permissions = ('change',)
    mark_not_featured.short_description = "Mark selected orders as not Featured"

    def mark_new(self, request, queryset):
        updated = queryset.update(new=True)
        self.message_user(request, ngettext(
            '%d product was successfully marked as New.',
            '%d products were successfully marked as New.',
            updated,
            ) % updated, messages.SUCCESS)
    mark_new.allowed_permissions = ('change',)
    mark_new.short_description = "Mark selected orders as New"

    def mark_old(self, request, queryset):
        updated = queryset.update(new=False)
        self.message_user(request, ngettext(
            '%d product was successfully marked as Old.',
            '%d products were successfully marked as Old.',
            updated,
            ) % updated, messages.SUCCESS)
    mark_old.allowed_permissions = ('change',)
    mark_old.short_description = "Mark selected orders as Old"



admin.site.register(Type)
admin.site.register(Category)
admin.site.register(Color)
admin.site.register(Product, ProductAdmin)
admin.site.register(Review)
admin.site.register(Size)
