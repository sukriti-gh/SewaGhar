from django import forms
from .models import VendorRequest
from .models import Feedback

class VendorRequestForm(forms.ModelForm):
    photo = forms.ImageField(label='Upload Your Image', required=False)
    photo1 = forms.ImageField(label='Upload Citizenship', required=False)
    photo2 = forms.ImageField(label='Upload Citizenship', required=False)
    class Meta:
        model = VendorRequest
        fields = [
            'business_name',
            'business_address',
            'contact_number',
            'email',
            'business_description',
            'business_category',
            'photo',
            'photo1',
            'photo2',
        ]

class MyFeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['by', 'message', 'type']
