from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.views.generic import CreateView, FormView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.contrib.auth import get_user_model
from .forms import UserRegisterForm, ServiceRegisterForm, UserLoginForm
from .models import AutoService

User = get_user_model()


class UserRegisterView(CreateView):
    form_class = UserRegisterForm
    template_name = 'account/user_register.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        try:
            # Сохраняем пользователя с ролью клиента
            user = form.save(commit=False)
            user.role = 'customer'  # Явно указываем роль
            user.save()

            # Автоматический вход после регистрации
            login(self.request, user)
            messages.success(self.request, 'Регистрация прошла успешно! Добро пожаловать!')
            return super().form_valid(form)

        except Exception as e:
            messages.error(self.request, f'Ошибка при регистрации: {str(e)}')
            return self.form_invalid(form)


class ServiceRegisterView(CreateView):
    form_class = ServiceRegisterForm
    template_name = 'account/service_register.html'

    def form_valid(self, form):
        try:
            # Создаем пользователя с ролью сервиса
            user = form.save(commit=False)
            user.role = 'service'
            user.save()

            # Создаем связанный автосервис
            service = AutoService.objects.create(
                user=user,
                name=form.cleaned_data['name'],
                address=form.cleaned_data['address'],
                phone=form.cleaned_data['phone'],
                description=form.cleaned_data.get('description', '')
            )

            # Автоматический вход
            login(self.request, user)
            messages.success(self.request, 'Регистрация сервиса прошла успешно!')

            # Редирект на страницу сервиса
            return redirect('services:service_detail', pk=service.pk)

        except Exception as e:
            # Откатываем изменения при ошибке
            if user.pk:
                user.delete()
            messages.error(self.request, f'Ошибка при регистрации сервиса: {str(e)}')
            return self.form_invalid(form)


class UserLoginView(FormView):
    form_class = UserLoginForm
    template_name = 'account/login.html'

    def form_valid(self, form):
        try:
            user = form.get_user()
            login(self.request, user)

            # Редирект в зависимости от роли
            if user.is_superuser:
                return redirect('dashboard:dashboard')

            elif user.role == 'manager':
                return redirect('dashboard:dashboard')

            elif user.role == 'service':
                try:
                    service = AutoService.objects.get(user=user)
                    return redirect('services:service_detail', pk=service.pk)
                except AutoService.DoesNotExist:
                    messages.warning(self.request, 'Профиль сервиса не найден')
                    return redirect('services:create_service')

            # Для обычных пользователей
            messages.success(self.request, f'Добро пожаловать, {user.username}!')
            return redirect('home')

        except Exception as e:
            messages.error(self.request, f'Ошибка входа: {str(e)}')
            return self.form_invalid(form)