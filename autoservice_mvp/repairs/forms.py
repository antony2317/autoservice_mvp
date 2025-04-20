# repairs/forms.py

from django import forms
from garage.models import Car
from .models import RepairRequest, RepairResponse


class RepairRequestForm(forms.ModelForm):
    class Meta:
        model = RepairRequest
        fields = ['car', 'description']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Получаем пользователя
        super().__init__(*args, **kwargs)

        if user:
            self.fields['car'].queryset = Car.objects.filter(user=user)  # Фильтрация по пользователю

class RepairResponseForm(forms.ModelForm):
    class Meta:
        model = RepairResponse
        fields = ['proposed_price', 'proposed_date']
        widgets = {
            'proposed_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'proposed_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
