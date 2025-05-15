from django import forms
from account.models import AutoService
from .models import Service, Master
from django.forms import modelformset_factory
from django.forms import DateTimeInput



class AutoServiceProfileForm(forms.ModelForm):
    class Meta:
        model = AutoService
        fields = ['name', 'address', 'phone']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }



class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'price']


class MasterForm(forms.ModelForm):
    class Meta:
        model = Master
        fields = ['name', 'specialization', 'experience']

#
# class BookingForm(forms.Form):
#     service = forms.ModelChoiceField(queryset=Service.objects.none(), label="Услуга")
#     date = forms.DateField(widget=forms.SelectDateWidget(), label="Дата")
#     time = forms.ChoiceField(choices=[], label="Время")
#
#     def __init__(self, *args, **kwargs):
#         autoservice = kwargs.pop('autoservice', None)
#         selected_date = kwargs.get('data', {}).get('date') or kwargs.get('initial', {}).get('date')
#         super().__init__(*args, **kwargs)
#
#         if autoservice:
#             self.fields['service'].queryset = autoservice.services.all()
#
#         if autoservice and selected_date:
#             time_slots = get_available_time_slots(autoservice, selected_date)
#             self.fields['time'].choices = [(slot, slot) for slot in time_slots]
#
#             class Meta:
#                 model = Booking
#                 fields = ['service', 'date', 'time']
#                 widgets = {
#                     'date': forms.DateInput(attrs={'type': 'date'}),
#                     'time': forms.Select(),  # будет динамически заполняться
#                 }

# WorkingHoursFormSet = modelformset_factory(
#     WorkingHours,
#     fields=('days_of_week', 'start_time', 'end_time'),
#     extra=0,
#     can_delete=False,
#     widgets={
#         'start_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
#         'end_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
#     }
# )