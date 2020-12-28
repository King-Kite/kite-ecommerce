from django import forms
from .models import Review


RATING_CHOICES = (
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
    )

class ReviewForm(forms.Form):
    body = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'Type your review here...',
        'cols': 7,
        'rows': 5
        }))
    rating = forms.ChoiceField(widget=forms.RadioSelect(attrs={
        'class' : 'form-check-input',
        }), choices=RATING_CHOICES)
