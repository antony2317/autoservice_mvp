
from .models import ServiceRecord, Garage


from django import forms
from .models import Car
from .constants import CAR_BRANDS

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['brand', 'model', 'year', 'vin', 'mileage']
        widgets = {
            'brand': forms.Select(attrs={
                'id': 'id_brand',
                'class': 'form-control',
                'onchange': 'loadModels()'
            }),
            'model': forms.TextInput(attrs={
                'id': 'id_model',
                'class': 'form-control',
                'list': 'model_list',
                'disabled': True
            }),
        }



class ServiceRecordForm(forms.ModelForm):
    garage_name = forms.CharField(
        label='Автосервис',
        required=False,
        widget=forms.TextInput(attrs={
            'autocomplete': 'off',
            'placeholder': 'Начните вводить название',
            'class': 'form-control'
        })
    )

    class Meta:
        model = ServiceRecord
        exclude = ['garage', 'created_by']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
        labels = {
            'date': 'Дата обслуживания',
            'mileage': 'Пробег',
            'description': 'Описание работ',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.garage:
            self.initial['garage_name'] = self.instance.garage.name

        for field_name, field in self.fields.items():
            if field_name not in ['garage', 'garage_name']:  # У нас уже есть свой input для garage_name
                field.widget.attrs.setdefault('class', 'form-control')

    def clean(self):
        cleaned_data = super().clean()
        garage_name = cleaned_data.get('garage_name', '').strip()

        if garage_name:
            garage, _ = Garage.objects.get_or_create(
                name=garage_name,
                defaults={'address': '', 'phone': ''}
            )
            cleaned_data['garage'] = garage
        else:
            cleaned_data['garage'] = None

        return cleaned_data