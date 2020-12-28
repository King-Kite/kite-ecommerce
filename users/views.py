from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views.generic import FormView, View
from .forms import BillingForm, ContactUsForm, UserUpdateForm, ProfileForm, ShippingForm
from .models import Address, Profile


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid

class ContactUsView(FormView):
    form_class = ContactUsForm
    template_name = 'pages/contact.html'
    success_url = '/'

    def form_valid(self, form):
        human = True
        form.clean()
        messages.success(self.request, 'Your message has been sent.')
        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, UserPassesTestMixin, View):
    model = Profile
    template_name = 'pages/profile.html'

    def get(self, request, *args, **kwargs):
        profile = Profile.objects.get(user=request.user)
        cart_item_list = request.user.useritems.filter(ordered=False)[:2]
        wishlist = request.user.wishlist.all()[:2]
        active = request.user.user_orders.filter(
                Q(user=request.user, ordered=True, status='P') |
                Q(user=request.user, ordered=True, status='BD')|
                Q(user=request.user, ordered=True, status='RR')
            ).order_by('-update_date')
        active_orders = active[:2]
        inactive = request.user.user_orders.filter(
            Q(user=request.user, ordered=True, status='D')|
            Q(user=request.user, ordered=True, status='RG')
        ).order_by('-update_date')
        inactive_orders = inactive[:2]
        billing_address = profile.user.address.filter(user=request.user, address_type='B', default=True).first()
        shipping_address = profile.user.address.filter(user=request.user, address_type='S', default=True).first()
        context = {
            'profile': profile,
            'cart_item_list': cart_item_list,
            'wishlist': wishlist,
            'active_orders': active_orders,
            'active_orders_count': active.count(),
            'inactive_orders': inactive_orders,
            'inactive_orders_count': inactive.count(),
            'billing_address': billing_address,
            'shipping_address': shipping_address,
            'site_name': 'Kite',
        }
        return render(request, self.template_name, context)

    def test_func(self):
        profile = Profile.objects.get(user=self.request.user)
        if self.request.user == profile.user:
            return True
        return False


class ProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'pages/profile-update.html'

    def get(self, request, *args, **kwargs):
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileForm(instance=request.user.profile)
        user_bill_add = request.user.address.filter(address_type='B', default=True).first()
        user_ship_add = request.user.address.filter(address_type='S', default=True).first()
        if user_bill_add is not None:
            bill_instance = {
                'billing_address1': user_bill_add.address1,
                'billing_address2': user_bill_add.address2,
                'billing_country': user_bill_add.country,
                'billing_state': user_bill_add.state,
                'billing_city': user_bill_add.city,
                'billing_zipcode': user_bill_add.zipcode
            }
        else:
            bill_instance = {}
        if user_ship_add is not None:
            ship_instance = {
                'shipping_address1': user_ship_add.address1,
                'shipping_address2': user_ship_add.address2,
                'shipping_country': user_ship_add.country,
                'shipping_state': user_ship_add.state,
                'shipping_city': user_ship_add.city,
                'shipping_zipcode': user_ship_add.zipcode
            }
        else:
            ship_instance = {}
        b_form = BillingForm(initial=bill_instance)
        s_form = ShippingForm(initial=ship_instance)
        context = {
            'u_form': u_form,
            'p_form': p_form,
            'b_form': b_form,
            's_form': s_form,
            'site_name': 'Kite',
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        user_bill_add = request.user.address.filter(address_type='B', default=True).first()
        user_ship_add = request.user.address.filter(address_type='S', default=True).first()
        if user_bill_add is not None:
            bill_instance = {
                'billing_address1': user_bill_add.address1,
                'billing_address2': user_bill_add.address2,
                'billing_country': user_bill_add.country,
                'billing_state': user_bill_add.state,
                'billing_city': user_bill_add.city,
                'billing_zipcode': user_bill_add.zipcode
            }
        else:
            bill_instance = {}
        if user_ship_add is not None:
            ship_instance = {
                'shipping_address1': user_ship_add.address1,
                'shipping_address2': user_ship_add.address2,
                'shipping_country': user_ship_add.country,
                'shipping_state': user_ship_add.state,
                'shipping_city': user_ship_add.city,
                'shipping_zipcode': user_ship_add.zipcode
            }
        else:
            ship_instance = {}
        b_form = BillingForm(request.POST, initial=bill_instance)
        s_form = ShippingForm(request.POST, initial=ship_instance)
        context = {
            'u_form': u_form,
            'p_form': p_form,
            'b_form': b_form,
            's_form': s_form,
            'site_name': 'Kite',
        }
        if u_form.is_valid() and p_form.is_valid() and b_form.is_valid() and s_form.is_valid():
            u_form.save()
            p_form.save()
            if user_bill_add is not None:
                user_bill_add.address1 = b_form.cleaned_data.get('billing_address1')
                user_bill_add.address2 = b_form.cleaned_data.get('billing_address2')
                user_bill_add.country = b_form.cleaned_data.get('billing_country')
                user_bill_add.state = b_form.cleaned_data.get('billing_state')
                user_bill_add.city = b_form.cleaned_data.get('billing_city')
                user_bill_add.zipcode = b_form.cleaned_data.get('billing_zipcode')
                user_bill_add.save()
            else:
                if is_valid_form([b_form.cleaned_data['billing_address1'], b_form.cleaned_data['billing_address2'], b_form.cleaned_data['billing_country'], b_form.cleaned_data['billing_state'], b_form.cleaned_data['billing_city'], b_form.cleaned_data['billing_zipcode']]):
                    Address.objects.get_or_create(
                            user = request.user,
                            address1 = b_form.cleaned_data.get('billing_address1'),
                            address2 = b_form.cleaned_data.get('billing_address2'),
                            country = b_form.cleaned_data.get('billing_country'),
                            state = b_form.cleaned_data.get('billing_state'),
                            city = b_form.cleaned_data.get('billing_city'),
                            zipcode = b_form.cleaned_data.get('billing_zipcode'),
                            address_type = 'B',
                            default=True
                            )
            if user_ship_add is not None:
                user_ship_add.address1 = s_form.cleaned_data.get('shipping_address1')
                user_ship_add.address2 = s_form.cleaned_data.get('shipping_address2')
                user_ship_add.country = s_form.cleaned_data.get('shipping_country')
                user_ship_add.state = s_form.cleaned_data.get('shipping_state')
                user_ship_add.city = s_form.cleaned_data.get('shipping_city')
                user_ship_add.zipcode = s_form.cleaned_data.get('shipping_zipcode')
                user_ship_add.save()
            else:
                if is_valid_form([s_form.cleaned_data['shipping_address1'], s_form.cleaned_data['shipping_address2'], s_form.cleaned_data['shipping_country'], s_form.cleaned_data['shipping_state'], s_form.cleaned_data['shipping_city'], s_form.cleaned_data['shipping_zipcode']]):
                    Address.objects.get_or_create(
                            user = request.user,
                            address1 = s_form.cleaned_data.get('shipping_address1'),
                            address2 = s_form.cleaned_data.get('shipping_address2'),
                            country = s_form.cleaned_data.get('shipping_country'),
                            state = s_form.cleaned_data.get('shipping_state'),
                            city = s_form.cleaned_data.get('shipping_city'),
                            zipcode = s_form.cleaned_data.get('shipping_zipcode'),
                            address_type = 'S',
                            default=True
                            )
            messages.success(request, f'Your Profile Update was successful!')
            return redirect('profile')
        return render(request, self.template_name, context)

    def test_func(self):
        profile = Profile.objects.get(user=self.request.user)
        if self.request.user == profile.user:
            return True
        return False
