import random, string
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.generic import ListView, RedirectView, TemplateView, View
from make_payments.models import Payments
from orders.models import CartItem, Order
from products.models import Product, ProductVariant
from users.models import Address
from .forms import CheckoutForm
from .models import Order, OrderProductInstance

User = get_user_model()

def create_ref_code(request):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


class AddToCartView(LoginRequiredMixin, RedirectView):
    url = '/cart/'
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        product = get_object_or_404(ProductVariant, pk=kwargs['pk'])
        cart_item = CartItem.objects.filter(user=self.request.user, product=product, ordered=False)
        if cart_item.exists():
            product_item = cart_item.first()
            product_item.quantity += 1
            product_item.save()
            messages.info(self.request, "This product quantity was updated.")
            return super().get_redirect_url(*args, **kwargs)
        else:
            CartItem.objects.create(user=self.request.user, product=product, ordered=False)
            messages.info(self.request, "This product was added to your cart.")
            return super().get_redirect_url(*args, **kwargs)


class CartView(LoginRequiredMixin, ListView):
    model = CartItem
    template_name = 'pages/cart.html'
    context_object_name = 'cart_item_list'

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user, ordered=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['original_price'] = CartItem.objects.get_original_price(user=self.request.user)
        context['final_price'] = CartItem.objects.get_final_price(user=self.request.user)
        context['get_total_discount'] = CartItem.objects.get_total_discount(user=self.request.user)
        context['site_name'] = 'Kite'
        return context


class CheckoutView(LoginRequiredMixin, View):
    template_name = 'pages/checkout.html'

    def get(self, request, *args, **kwargs):
        form = CheckoutForm()

        try:
            cart_item_list = CartItem.objects.filter(user=self.request.user, ordered=False)
            if cart_item_list:
                sum = 0
                for item in cart_item_list:
                    if item.product.discount_price:
                        total = item.product.discount_price * item.quantity
                    else:
                        total = item.product.price * item.quantity
                    sum += total
                context = {
                    'form': form,
                    'cart_item_list': cart_item_list,
                    'cart_item_list_total': sum,
                    'site_name': 'Kite',
                }

                billing_address_queryset = Address.objects.check_default_billing_address(request.user)
                if billing_address_queryset is not None:
                    context.update({ 'default_billing_address' : billing_address_queryset[0] })

                shipping_address_queryset = Address.objects.check_default_shipping_address(request.user)
                if shipping_address_queryset is not None:
                    context.update({ 'default_shipping_address' : shipping_address_queryset[0] })

                return render(request, self.template_name, context)
            else:
                messages.error(request, 'You do not have any product in your cart.')
                return redirect('cart')
        except ObjectDoesNotExist:
            messages.error(request, 'You do not have any product in your cart.')
            return redirect('cart')

    def post(self, request, *args, **kwargs):
        form = CheckoutForm(request.POST or None)
        try:
            cart_item_list = CartItem.objects.filter(user=self.request.user, ordered=False)
            order = Order.objects.create(
                user = request.user
                )
            order.products.set(cart_item_list)
            if form.is_valid():
                set_default_billing = form.cleaned_data.get("set_default_billing")
                use_default_billing = form.cleaned_data.get("use_default_billing")

                if use_default_billing:
                    billing_address_queryset = Address.objects.check_default_billing_address(request.user)
                    if billing_address_queryset:
                        billing_address = billing_address_queryset[0]
                        billing_address.save()
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(request, 'No default billing address available')
                        return redirect('checkout')
                else:
                    if is_valid_form([form.cleaned_data['billing_address1'], form.cleaned_data['billing_address2'], form.cleaned_data['billing_country_code'], form.cleaned_data['billing_state'], form.cleaned_data['billing_city'], form.cleaned_data['billing_zipcode']]):

                        billing_address = Address(
                            user = request.user,
                            address1 = form.cleaned_data.get("billing_address1"),
                            address2 = form.cleaned_data.get("billing_address2"),
                            country = form.cleaned_data.get("billing_country_code"),
                            state = form.cleaned_data.get("billing_state"),
                            city = form.cleaned_data.get("billing_city"),
                            zipcode = form.cleaned_data.get("billing_zipcode"),
                            address_type = 'B'
                            )
                        billing_address.save()

                        if set_default_billing:
                            billing_address_queryset = Address.objects.check_default_billing_address(request.user)
                            if billing_address_queryset:
                                default_billing = billing_address_queryset[0]
                                default_billing.default = False
                                default_billing.save()
                                billing_address.default = True
                                billing_address.save()
                            else:
                                billing_address.default = True
                                billing_address.save()

                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(request, 'Please fill in the required billing address fields')
                        return redirect('checkout')

                use_default_shipping = form.cleaned_data.get("use_default_shipping")
                same_shipping_address = form.cleaned_data.get("same_shipping_address")
                if same_shipping_address:
                    shipping_address = billing_address
                    shipping_address.pk = None
                    shipping_address.save()
                    shipping_address.address_type = 'S'
                    shipping_address.save()
                    order.shipping_address = shipping_address
                    order.save()
                elif use_default_shipping:
                    shipping_address_queryset = Address.objects.check_default_shipping_address(request.user)
                    if shipping_address_queryset:
                        shipping_address = shipping_address_queryset[0]
                        shipping_address.save()
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(request, 'No default shipping address available')
                        return redirect('checkout')
                else:
                    if is_valid_form([form.cleaned_data['shipping_address1'], form.cleaned_data['shipping_address2'], form.cleaned_data['shipping_country_code'], form.cleaned_data['shipping_state'], form.cleaned_data['shipping_city'], form.cleaned_data['shipping_zipcode']]):

                        shipping_address = Address(
                            user = request.user,
                            address1 = form.cleaned_data.get("shipping_address1"),
                            address2 = form.cleaned_data.get("shipping_address2"),
                            country = form.cleaned_data.get("shipping_country_code"),
                            state = form.cleaned_data.get("shipping_state"),
                            city = form.cleaned_data.get("shipping_city"),
                            zipcode = form.cleaned_data.get("shipping_zipcode"),
                            address_type = 'S'
                            )
                        shipping_address.save()
                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get("set_default_shipping")
                        if set_default_shipping:
                            shipping_address_queryset = Address.objects.check_default_shipping_address(request.user)
                            if shipping_address_queryset:
                                default_shipping = shipping_address_queryset[0]
                                default_shipping.default = False
                                default_shipping.save()
                                shipping_address.default = True
                                shipping_address.save()
                            else:
                                shipping_address.default = True
                                shipping_address.save()
                    else:
                        messages.info(request, 'Please fill in the required shipping address fields')

                payment_option = form.cleaned_data.get('payment_option')
                if payment_option == 'S':
                    messages.info(request, 'This payment option is currently not available. Try the dummy option.')
                    return redirect('checkout')
                elif payment_option == 'P':
                    messages.info(request, 'This payment option is currently not available. Try the dummy option.')
                    return redirect('checkout')
                elif payment_option == 'D':
                    payment = Payments.objects.create(
                        user = request.user,
                        variant = 'default',
                        status = 'confirmed',
                        transaction_id = create_ref_code(request),
                        currency = 'ngn',
                        total = order.get_total(),
                        billing_first_name = request.user.first_name,
                        billing_last_name = request.user.last_name,
                        billing_address_1 = form.cleaned_data.get("billing_address1"),
                        billing_address_2 = form.cleaned_data.get("billing_address1"),
                        billing_city = form.cleaned_data.get("billing_city"),
                        billing_postcode = form.cleaned_data.get("billing_zipcode"),
                        billing_country_code = form.cleaned_data.get("billing_country_code"),
                        billing_email = request.user.email,
                        customer_ip_address = '127.0.0.1'
                    )
                    payment.save()
                    order.payment = payment
                    # TODO: assign reference code
                    order.ref_code = payment.transaction_id
                    order.ordered = True
                    order.save()
                    cart_items = order.products.all()
                    cart_items.update(ordered=True)
                    for product in cart_items:
                        product.ordered = True
                        product.save()
                    for item in order.products.all():
                        OrderProductInstance.objects.get_or_create(
                            user = request.user,
                            order = order,
                            ordered = order.ordered,
                            product_name = item.product.parent.name,
                            product_image = item.product.parent.image,
                            product_price = item.product.price,
                            product_size = item.product.size,
                            quantity = item.quantity,
                            create_date = order.ordered_date
                        )
                    messages.success(self.request, "Your order was successful!")
                    return redirect('order-summary')
                else:
                    messages.warning(self.request, 'Invalid Payment Option Selected.')
                    return redirect('checkout')
                return redirect('cart')
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order.")
            return redirect('cart')


class OrderSummaryView(LoginRequiredMixin, TemplateView):
    models = OrderProductInstance
    template_name = 'pages/order-summary.html'

    def get_context_data(self, **kwargs):
        try:
            user_active_order = OrderProductInstance.objects.filter(
                Q(user=self.request.user, ordered=True, status='P') |
                Q(user=self.request.user, ordered=True, status='BD')|
                Q(user=self.request.user, ordered=True, status='RR')
            ).order_by('-update_date')

            user_inactive_order = OrderProductInstance.objects.filter(
                Q(user=self.request.user, ordered=True, status='D') |
                Q(user=self.request.user, ordered=True, status='RG')
            ).order_by('-update_date')

            context = super().get_context_data(**kwargs)
            context['user_active_order'] = user_active_order
            context['user_inactive_order'] = user_inactive_order
            context['site_name'] = 'Kite'
            return context
        except ObjectDoesNotExist:
            messages.error(request, "You do not have an active order.")
            return redirect('cart')


class RemoveFromCartView(LoginRequiredMixin, RedirectView):
    url = '/cart/'
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        product = get_object_or_404(ProductVariant, pk=kwargs['pk'])
        cart_item = CartItem.objects.filter(user=self.request.user, product=product, ordered=False)
        if cart_item.exists():
            product_item = cart_item.first()
            product_item.delete()
            messages.info(self.request, "This product was removed from your cart.")
            return super().get_redirect_url(*args, **kwargs)
        else:
            messages.info(self.request, "This product was not in your cart.")
            return super().get_redirect_url(*args, **kwargs)


class RemoveSingleProductFromCartView(LoginRequiredMixin, RedirectView):
    url = '/cart/'
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        product = get_object_or_404(ProductVariant, pk=kwargs['pk'])
        cart_item = CartItem.objects.filter(user=self.request.user, product=product, ordered=False)
        if cart_item.exists():
            product_item = cart_item.first()
            if product_item.quantity > 1:
                product_item.quantity -= 1
                product_item.save()
            else:
                product_item.delete()
            messages.info(self.request, "This product quantity was updated.")
            return super().get_redirect_url(*args, **kwargs)
        else:
            messages.info(self.request, "This product was not in your short.")
            return redirect('product-info', slug=product_item.parent.slug)
