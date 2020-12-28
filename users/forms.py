from allauth.account.forms import SignupForm, LoginForm
from captcha.fields import CaptchaField
from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.forms import ClearableFileInput
from django.utils.translation import ugettext_lazy
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from .models import Address, ContactUs, Profile

User = get_user_model()

class ContactUsForm(forms.ModelForm):
    captcha = CaptchaField()
    class Meta:
        model = ContactUs
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Name',
                }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'E-mail',
                }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subject',
                }),
            'message': forms.Textarea(attrs={
                    'class': 'form-control',
                    'placeholder': 'Type message here...',
                    'rows': 4
                }),
        }

    def clean(self):
        cleaned_data = super(ContactUsForm, self).clean()
        name = cleaned_data.get('name')
        email = cleaned_data.get('email')
        subject = cleaned_data.get('subject')
        message = cleaned_data.get('message')

        if not name:
            raise ValidationError("This field is required.")
        if not email:
            raise ValidationError("This field is required.")
        elif email:
            validate_email(email)
            # validate_email.message = 'Please Enter a Valid Email Address'
        if not subject:
            raise ValidationError("This field is required.")
        if not message:
            raise ValidationError("This field is required.")

        if name and email and subject and message:
            ContactUs.objects.get_or_create(
                name = name,
                email = email,
                subject = subject,
                message = message
                )
        return cleaned_data


class SignInForm(LoginForm):

    def __init__(self, *args, **kwargs):
        super(SignInForm, self).__init__(*args, **kwargs)
        self.fields['login'].widget.attrs['class'] = 'form-control'
        self.fields['login'].widget.attrs['placeholder'] = 'Username or E-mail'
        self.fields['password'].widget.attrs['class'] = 'form-control'
        self.fields['password'].widget.attrs['placeholder'] = 'Password'


class SignUpForm(SignupForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'First Name',
        'class' : 'form-control'
        }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Last Name',
        'class': 'form-control'
        }))
    # phone = PhoneNumberField(help_text='e.g (+2341234567890)')
    # check why adding other fields won't work or allow verrification

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['placeholder'] = 'E-mail'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = 'Enter Password'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = 'Enter Password Again'

    def signup(self, request, user):
        user = request.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField()
    last_name = forms.CharField()

    class Meta:
        model = User
        fields = ['first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['class'] = 'form-control'
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
        self.fields['last_name'].widget.attrs['class'] = 'form-control'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter Last Name'


class MyImageWidget(ClearableFileInput):
    template_name = 'pages/image_template.html'


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image', 'age', 'sex', 'country', 'state', 'city', 'address', 'zip_code']
        widgets = {
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your contact address',
                'rows': 3,
                'cols': 6,
                }),
            'image': MyImageWidget(),
            'age': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter age',
            }),
            'sex': forms.RadioSelect(),
            'country': CountrySelectWidget(attrs={
                'class': 'form-control'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter state e.g. Kwara, Lagos',
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter city e.g. Ilorin, Ikeja',
            }),
            'zip_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Zip Code e.g. 240242',
            })
        }


class BillingForm(forms.Form):
    billing_address1 = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter Street Address...',
        }))
    billing_address2 = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter Apartment Address...',
        }))
    billing_country = CountryField(blank=True, blank_label='(select country)').formfield(required=False, label='Country', widget=CountrySelectWidget(attrs={
        'class': 'form-control'
        }))
    billing_state = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter State...',
        }))
    billing_city = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter City...',
        }))
    billing_zipcode = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter Zip Code...',
        }))


class ShippingForm(forms.Form):
    shipping_address1 = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter Street Address...',
        }))
    shipping_address2 = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter Apartment Address...',
        }))
    shipping_country = CountryField(blank=True, blank_label='(select country)').formfield(required=False, label='Country', widget=CountrySelectWidget(attrs={
        'class': 'form-control'
        }))
    shipping_state = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter State...',
        }))
    shipping_city = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter City...',
        }))
    shipping_zipcode = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter Zip Code...',
        }))

