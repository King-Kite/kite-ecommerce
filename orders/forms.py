from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

PAYMENT_CHOICES = (
    ('P', 'Paypal'),
    ('S', 'Stripe'),
    ('D', 'Dummy'),
    )


class CheckoutForm(forms.Form):
    billing_address1 = forms.CharField(required=False)
    billing_address2 = forms.CharField(required=False)
    billing_country_code = CountryField(blank=True, blank_label='(select country)').formfield(required=False, label='Country', widget=CountrySelectWidget(attrs={
        'placeholder': 'select country',
        'class': 'form-control'
        }))
    billing_state = forms.CharField(required=False)
    billing_city = forms.CharField(required=False)
    billing_zipcode = forms.CharField(required=False)
    same_shipping_address = forms.BooleanField(required=False)
    set_default_billing = forms.BooleanField(required=False)
    use_default_billing = forms.BooleanField(required=False)

    shipping_address1 = forms.CharField(required=False)
    shipping_address2 = forms.CharField(required=False)
    shipping_country_code = CountryField(blank=True, blank_label='(select country)').formfield(required=False, label='Country', widget=CountrySelectWidget(attrs={
        'placeholder': 'select country',
        'class': 'form-control'
        }))
    shipping_state = forms.CharField(required=False)
    shipping_city = forms.CharField(required=False)
    shipping_zipcode = forms.CharField(required=False)
    set_default_shipping = forms.BooleanField(required=False)
    use_default_shipping = forms.BooleanField(required=False)

    payment_option = forms.ChoiceField(widget=forms.RadioSelect, choices=PAYMENT_CHOICES)


class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={
        'row': 4
        }))
    email = forms.EmailField()
