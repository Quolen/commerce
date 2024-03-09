from django import forms
from django.core.exceptions import ValidationError

def validate_bid(value):
    if value <= 0:
        raise ValidationError('Bid must be greater than zero.')

class ListingForm(forms.Form):
    title = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Enter your title'}), required=True)
    desc = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Enter listing description', 'class': 'form-control'}), required=True)
    bid = forms.DecimalField(max_digits=10, decimal_places=2, required=True, validators=[validate_bid])
    image = forms.ImageField(required=False)
    category = forms.CharField(max_length=50, required=False)