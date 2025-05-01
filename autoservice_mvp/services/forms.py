from django import forms
from account.models import AutoService

class AutoServiceProfileForm(forms.ModelForm):
    class Meta:
        model = AutoService
        fields = ['name', 'address', 'phone']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }
