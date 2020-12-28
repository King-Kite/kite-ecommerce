from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from .models import Address, ContactUs, CustomUser, Profile
from django.utils.translation import gettext_lazy as _


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False


class ContactUsAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'read', 'replied' , 'create_date', 'replied_date']

    list_filter = ['name', 'email', 'read', 'replied' , 'create_date', 'replied_date']

    actions = ['mark_read', 'mark_not_read', 'mark_replied', 'mark_not_replied']

    def mark_read(self, request, queryset):
        updated = queryset.update(read=True)
        self.message_user(request, ngettext(
            '%d message was successfully marked as Read.',
            '%d messages were successfully marked as Read.',
            updated,
            ) % updated, messages.SUCCESS)
    mark_read.allowed_permissions = ('change',)
    mark_read.short_description = "Mark selected orders as Read"

    def mark_not_read(self, request, queryset):
        updated = queryset.update(read=False)
        self.message_user(request, ngettext(
            '%d message was successfully marked as not Read.',
            '%d messages were successfully marked as not Read.',
            updated,
            ) % updated, messages.SUCCESS)
    mark_not_read.allowed_permissions = ('change',)
    mark_not_read.short_description = "Mark selected orders as not Read"

    def mark_replied(self, request, queryset):
        updated = queryset.update(replied=True)
        self.message_user(request, ngettext(
            '%d message was successfully marked as Replied.',
            '%d messages were successfully marked as Replied.',
            updated,
            ) % updated, messages.SUCCESS)
    mark_replied.allowed_permissions = ('change',)
    mark_replied.short_description = "Mark selected orders as Replied"

    def mark_not_replied(self, request, queryset):
        updated = queryset.update(replied=False)
        self.message_user(request, ngettext(
            '%d message was successfully marked as not Replied.',
            '%d messages were successfully marked as not Replied.',
            updated,
            ) % updated, messages.SUCCESS)
    mark_not_replied.allowed_permissions = ('change',)
    mark_not_replied.short_description = "Mark selected orders as not Replied"

class CustomUserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'is_staff']
    list_filter = ['is_staff']
    search_fields = ['username', 'email']
    ordering = ['username', 'email']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    inlines = (ProfileInline,)

class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'address1', 'address2', 'country' , 'state', 'city', 'zipcode', 'address_type', 'default'
    ]
    list_filter = [
        'user', 'address1', 'address2', 'country' , 'state', 'city', 'zipcode', 'address_type', 'default'
    ]
    search_fields = [
        'user', 'address1', 'address2', 'country' , 'state', 'city', 'zipcode', 'address_type'
    ]


admin.site.register(Address, AddressAdmin)
admin.site.register(ContactUs, ContactUsAdmin)
admin.site.register(Profile)
admin.site.register(CustomUser, CustomUserAdmin)
