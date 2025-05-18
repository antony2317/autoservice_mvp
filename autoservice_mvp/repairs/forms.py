from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from garage.models import Car
from .models import RepairRequest, RepairResponse
from django.conf import settings


class RepairRequestForm(forms.ModelForm):
    class Meta:
        model = RepairRequest
        fields = ['car', 'description']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['car'].queryset = Car.objects.filter(user=user)

class RepairResponseForm(forms.ModelForm):
    class Meta:
        model = RepairResponse
        fields = ['proposed_price', 'proposed_date']
        widgets = {
            'proposed_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'proposed_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
