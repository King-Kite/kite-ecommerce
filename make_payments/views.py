import random, string

from django.shortcuts import render
from django.contrib.auth.decorators import login_required


from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from payments import get_payment_model, RedirectNeeded


@login_required
def create_ref_code(request):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

def payment_details(request, payment_id):
    payment = get_object_or_404(get_payment_model(), id=payment_id)
    try:
        form = payment.get_form(data=request.POST or None)
    except RedirectNeeded as redirect_to:
        return redirect(str(redirect_to))
    return render(request, 'pages/payment.html',{'form': form, 'payment': payment})


class PaymentsView(LoginRequiredMixin,View):
    form_class = PaymentsForm
    initial = {'key': 'value'}
    template_name = 'payment.html'

    def get(self, request, *args, **kwargs):
        try:
            form = self.form_class(initial=self.initial)
            order = Order.objects.get(user=request.user, ordered=False)
            context = {
                    'form': form,
                    'couponform': CouponForm(),
                    'shippingform': ShippingForm(),
                    'order': order,
                    # 'DISPLAY_COUPON_FORM': True
                }
            return render(request, self.template_name, context)
        except ObjectDoesNotExist:
            messages.info(request, "You do not have an active order.")
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, initial=self.initial)
        try:
            order = Order.objects.get(user=request.user, ordered=False)
            amount = int(order.get_total())
            if form.is_valid():
                billing_address_1 = form.cleaned_data['billing_address_1']
                billing_address_2 = form.cleaned_data['billing_address_2']
                billing_country_code = form.cleaned_data['billing_country_code']
                billing_city = form.cleaned_data['billing_city']
                billing_postcode = form.cleaned_data['billing_postcode']
                # TODO: add functionality for these fields
                # same_shipping_address = form.cleaned_data['same_shipping_address']
                # save_info = form.cleaned_data['save_info']
                billing_address = Address(
                    user = self.request.user,
                    street_address = billing_address_1,
                    apartment_address = billing_address_2,
                    country = billing_country_code,
                    zip = billing_postcode,
                    address_type = 'B'
                    )
                billing_address.save()
                order.billing_address = billing_address
                payments = Payments.objects.create(
                    user = request.user,
                    variant = 'default',
                    status = 'confirmed',
                    transaction_id = create_ref_code(request),
                    currency = 'usd',
                    total = amount,
                    billing_first_name = request.user.first_name,
                    billing_last_name = request.user.last_name,
                    billing_address_1 = billing_address_1,
                    billing_address_2 = billing_address_2,
                    billing_city = billing_city,
                    billing_postcode = billing_postcode,
                    billing_country_code = billing_country_code,
                    billing_email = request.user.email,
                    customer_ip_address = '127.0.0.1'
                    )
                payments.save()
                order.payments = payments
                # TODO: assign reference code
                order.ref_code = payments.transaction_id
                order.ordered = True
                order.save()
                order_items = order.items.all()
                order_items.update(ordered=True)
                for item in order_items:
                    item.save()

                messages.success(self.request, "Your order was successful!")
                return redirect('home')
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order.")
            return redirect('order-summary')
        return render(request, self.template_name, {'form': form})
