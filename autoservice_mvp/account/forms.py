from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, AutoService
from django.utils.translation import gettext_lazy as _


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class ServiceRegisterForm(UserCreationForm):
    name = forms.CharField(
        max_length=100,
        required=True,
        label=_('Название автосервиса'),
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'ООО "АвтоСервис"',
            'autofocus': True
        })
    )

    address = forms.CharField(
        label=_('Адрес автосервиса'),
        widget=forms.Textarea(attrs={
            'class': 'form-input textarea-input',
            'placeholder': 'г. Москва, ул. Автозаводская, д. 10',
            'rows': 3
        })
    )

    phone = forms.CharField(
        max_length=20,
        required=True,
        label=_('Контактный телефон'),
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '+375 (XX) XXX-XX-XX'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'name', 'address', 'phone']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'autoservice2024'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'contact@autoservice.ru'
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'form-input password-input',
                'placeholder': 'Придумайте надежный пароль'
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-input password-input',
                'placeholder': 'Повторите пароль'
            }),
        }


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label='Email/Username')
