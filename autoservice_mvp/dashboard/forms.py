from django import forms
from garage.models import CarBase
from repairs.models import RepairCategory, RepairType

class CarBaseForm(forms.ModelForm):
    class Meta:
        model = CarBase
        fields = [
            'brand',
            'model',
            'generation',
            'year_from',
            'year_to',
            'engine_type',
            'engine_volume',
        ]
        widgets = {
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'generation': forms.TextInput(attrs={'class': 'form-control'}),
            'year_from': forms.NumberInput(attrs={'class': 'form-control'}),
            'year_to': forms.NumberInput(attrs={'class': 'form-control'}),
            'engine_type': forms.Select(attrs={'class': 'form-select'}),
            'engine_volume': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
        }




class RepairCategoryForm(forms.ModelForm):
    class Meta:
        model = RepairCategory
        fields = ['name']
        labels = {
            'name': 'Название категории',
        }


class RepairTypeForm(forms.ModelForm):
    class Meta:
        model = RepairType
        fields = ['category', 'name']
        labels = {
            'category': 'Категория',
            'name': 'Название типа ремонта',
        }
