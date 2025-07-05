
from .models import ServiceRecord, Garage, CarBase

from django import forms
from .models import Car
from django.db.models import Q
from datetime import datetime


class CarForm(forms.ModelForm):
    brand = forms.ChoiceField(label='Марка', required=True)
    model = forms.ChoiceField(label='Модель', required=True)
    year = forms.ChoiceField(label='Год выпуска', required=True)
    generation = forms.CharField(label='Поколение', required=False,
                                 widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    engine_type = forms.ChoiceField(label='Тип двигателя', required=True)

    engine_volume = forms.DecimalField(
        label='Объем двигателя (л)',
        required=False,
        max_digits=4,
        decimal_places=1,
        widget=forms.NumberInput(attrs={
            'step': '0.1',
            'min': '0',
            'placeholder': 'Например 1,9'
        })
    )

    class Meta:
        model = Car
        fields = ['vin', 'mileage', 'year']
        widgets = {
            'vin': forms.TextInput(attrs={'class': 'form-control'}),
            'mileage': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        data = self.data or self.initial
        brand = data.get('brand')
        model = data.get('model')
        year = data.get('year')

        # Марки
        brands = CarBase.objects.values_list('brand', flat=True).distinct().order_by('brand')
        self.fields['brand'].choices = [('', '---------')] + [(b, b) for b in brands]

        # Модели
        if brand:
            models_qs = CarBase.objects.filter(brand=brand).values_list('model', flat=True).distinct().order_by('model')
            self.fields['model'].choices = [('', '---------')] + [(m, m) for m in models_qs]
        else:
            self.fields['model'].choices = [('', '---------')]

        # Годы
        if brand and model:
            years_qs = CarBase.objects.filter(brand=brand, model=model)
            years = set()
            current_year = datetime.now().year
            for cb in years_qs:
                end_year = cb.year_to or current_year
                years.update(range(cb.year_from, end_year + 1))
            self.fields['year'].choices = [('', '---------')] + [(y, y) for y in sorted(years)]
        else:
            self.fields['year'].choices = [('', '---------')]

        # Тип двигателя — все возможные, не фильтруем
        engine_type_field = CarBase._meta.get_field('engine_type')
        self.fields['engine_type'].choices = [('', '---------')] + list(engine_type_field.choices)

        # Объем двигателя — фильтрация по марке, модели и году
        if brand and model and year:
            volumes_qs = CarBase.objects.filter(
                brand=brand,
                model=model,
                year_from__lte=year
            ).filter(
                Q(year_to__gte=year) | Q(year_to__isnull=True)
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

        if not all([brand, model, year]):
            raise forms.ValidationError('Пожалуйста, заполните все обязательные поля.')

        try:
            year = int(year)
        except (ValueError, TypeError):
            raise forms.ValidationError('Неверный формат года выпуска.')

        if engine_type != 'electric' and not engine_volume:
            self.add_error('engine_volume', 'Объем двигателя обязателен для данного типа двигателя.')

        try:
            # Без engine_type и engine_volume
            base_car = CarBase.objects.filter(
                brand=brand,
                model=model,
                year_from__lte=year
            ).filter(
                Q(year_to__gte=year) | Q(year_to__isnull=True)
            ).get()
        except CarBase.DoesNotExist:
            raise forms.ValidationError('Автомобиль с такими параметрами не найден в базе.')
        except CarBase.MultipleObjectsReturned:
            raise forms.ValidationError('Найдено несколько совпадений в базе. Уточните параметры.')

        cleaned_data['generation'] = base_car.generation or ''
        cleaned_data['base_car'] = base_car
        return cleaned_data

    def save(self, commit=True):
        car = super().save(commit=False)
        car.base_car = self.cleaned_data.get('base_car')
        car.year = int(self.cleaned_data.get('year'))
        car.engine_type = self.cleaned_data.get('engine_type')
        engine_volume = self.cleaned_data.get('engine_volume')
        car.engine_volume = engine_volume if engine_volume else None
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