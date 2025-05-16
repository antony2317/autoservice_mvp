
from .models import ServiceRecord



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
    class Meta:
        model = ServiceRecord
        exclude = ['autoservice', 'created_by']  # заменили 'garage' на 'autoservice' (или другое реальное поле)
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'mileage': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите пробег'
            }),
            'service_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например, Замена масла'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Описание выполненных работ (необязательно)'
            }),
            'cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Стоимость в рублях'
            }),
            'receipt': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'date': 'Дата обслуживания',
            'mileage': 'Пробег',
            'service_type': 'Вид работ',
            'description': 'Описание работ',
            'cost': 'Стоимость',
            'receipt': 'Чек (необязательно)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Применить базовый стиль Bootstrap ко всем полям
        for field in self.fields.values():
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