
from .models import ServiceRecord, Garage, CarBase

from django import forms
from .models import Car
from .constants import CAR_BRANDS


class CarForm(forms.ModelForm):
    brand = forms.ChoiceField(label='Марка', required=True)
    model = forms.ChoiceField(label='Модель', required=True)
    year = forms.ChoiceField(label='Год выпуска', required=True)
    engine_type = forms.ChoiceField(
        choices=[('', '---------')] + list(CarBase._meta.get_field('engine_type').choices),
        label='Тип двигателя',
        required=True
    )
    engine_volume = forms.ChoiceField(label='Объем двигателя (л)', required=True)

    class Meta:
        model = Car
        fields = ['vin', 'mileage', 'year']  # Добавляем year сюда, если есть в модели
        widgets = {
            'vin': forms.TextInput(attrs={'class': 'form-control'}),
            'mileage': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Получаем данные из POST или initial для динамической загрузки
        data = self.data or self.initial

        brand = data.get('brand')
        model = data.get('model')
        year = data.get('year')
        engine_type = data.get('engine_type')

        # Загрузка брендов (всегда)
        brands = CarBase.objects.values_list('brand', flat=True).distinct().order_by('brand')
        self.fields['brand'].choices = [('', '---------')] + [(b, b) for b in brands]

        # Заполняем модели в зависимости от бренда
        if brand:
            models = CarBase.objects.filter(brand=brand).values_list('model', flat=True).distinct().order_by('model')
            self.fields['model'].choices = [('', '---------')] + [(m, m) for m in models]
        else:
            self.fields['model'].choices = [('', '---------')]

        # Заполняем года в зависимости от бренда и модели
        if brand and model:
            years_qs = CarBase.objects.filter(brand=brand, model=model)
            years = set()
            for car_base in years_qs:
                years.update(range(car_base.year_from, car_base.year_to + 1))
            years = sorted(years)
            self.fields['year'].choices = [('', '---------')] + [(y, y) for y in years]
        else:
            self.fields['year'].choices = [('', '---------')]

        # Заполняем типы двигателя, если есть бренд, модель, год
        if brand and model and year:
            engine_types_qs = CarBase.objects.filter(
                brand=brand,
                model=model,
                year_from__lte=year,
                year_to__gte=year,
            ).values_list('engine_type', flat=True).distinct()
            engine_type_dict = dict(CarBase._meta.get_field('engine_type').choices)
            self.fields['engine_type'].choices = [('', '---------')] + [(et, engine_type_dict.get(et, et)) for et in engine_types_qs]
        else:
            self.fields['engine_type'].choices = [('', '---------')]

        # Заполняем объемы двигателя, если есть бренд, модель, год и тип двигателя
        if brand and model and year and engine_type:
            volumes_qs = CarBase.objects.filter(
                brand=brand,
                model=model,
                year_from__lte=year,
                year_to__gte=year,
                engine_type=engine_type,
            ).values_list('engine_volume', flat=True).distinct().order_by('engine_volume')
            self.fields['engine_volume'].choices = [('', '---------')] + [(str(v), str(v)) for v in volumes_qs]
        else:
            self.fields['engine_volume'].choices = [('', '---------')]

    def clean(self):
        cleaned_data = super().clean()
        brand = cleaned_data.get('brand')
        model = cleaned_data.get('model')
        year = cleaned_data.get('year')
        engine_type = cleaned_data.get('engine_type')
        engine_volume = cleaned_data.get('engine_volume')

        if not all([brand, model, year, engine_type, engine_volume]):
            raise forms.ValidationError('Пожалуйста, заполните все поля.')

        # Проверяем, что такой автомобиль есть в базе
        try:
            base_car = CarBase.objects.get(
                brand=brand,
                model=model,
                year_from__lte=year,
                year_to__gte=year,
                engine_type=engine_type,
                engine_volume=engine_volume,
            )
        except CarBase.DoesNotExist:
            raise forms.ValidationError('Автомобиль с такими параметрами не найден в базе.')

        cleaned_data['base_car'] = base_car
        return cleaned_data

    def save(self, commit=True):
        car = super().save(commit=False)
        car.base_car = self.cleaned_data.get('base_car')
        car.year = int(self.cleaned_data.get('year'))
        if commit:
            car.save()
        return car




class ServiceRecordForm(forms.ModelForm):
    class Meta:
        model = ServiceRecord
        exclude = ['autoservice', 'created_by']
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