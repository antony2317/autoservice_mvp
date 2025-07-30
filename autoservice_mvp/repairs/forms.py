from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from garage.models import Car
from .models import RepairRequest, RepairResponse, RepairCategory, RepairType
from django.conf import settings


class RepairRequestForm(forms.ModelForm):
    problem_not_listed = forms.BooleanField(
        required=False,
        label="Моей проблемы нет в списке"
    )

    class Meta:
        model = RepairRequest
        fields = ['car', 'category', 'repair_type', 'description', 'problem_not_listed']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Показываем только машины пользователя
        if user:
            self.fields['car'].queryset = Car.objects.filter(user=user)

        # Категория и тип ремонта
        self.fields['category'].queryset = RepairCategory.objects.all()
        self.fields['category'].empty_label = "Выберите категорию"

        self.fields['repair_type'].queryset = RepairType.objects.none()

        # Если передана категория — загружаем типы ремонта
        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['repair_type'].queryset = RepairType.objects.filter(category_id=category_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.category:
            self.fields['repair_type'].queryset = RepairType.objects.filter(category=self.instance.category)

    def clean(self):
        cleaned_data = super().clean()
        problem_not_listed = cleaned_data.get('problem_not_listed')
        category = cleaned_data.get('category')
        repair_type = cleaned_data.get('repair_type')
        description = cleaned_data.get('description')

        if problem_not_listed:
            if not description:
                self.add_error('description', 'Пожалуйста, опишите проблему, если не выбрали категорию.')
        else:
            if not category:
                self.add_error('category', 'Выберите категорию или отметьте, что проблемы нет в списке.')
            if not repair_type:
                self.add_error('repair_type', 'Выберите тип ремонта или отметьте, что проблемы нет в списке.')

class RepairResponseForm(forms.ModelForm):
    class Meta:
        model = RepairResponse
        fields = ['proposed_price', 'proposed_date']
        widgets = {
            'proposed_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'proposed_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
