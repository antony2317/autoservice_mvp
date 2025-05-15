from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.views.generic import CreateView, FormView
from django.urls import reverse_lazy, reverse
from .forms import UserRegisterForm, ServiceRegisterForm, UserLoginForm
from .models import AutoService



class UserRegisterView(CreateView):
    form_class = UserRegisterForm
    template_name = 'account/user_register.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save(commit=False)
        user.is_service = False
        user.save()
        login(self.request, user)
        return response


class ServiceRegisterView(CreateView):
    form_class = ServiceRegisterForm
    template_name = 'account/service_register.html'

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_service = True
        user.save()

        # Создаем сервис и сохраняем его в переменную
        service = AutoService.objects.create(
            user=user,
            name=form.cleaned_data['name'],
            address=form.cleaned_data['address'],
            phone=form.cleaned_data['phone']
        )

        login(self.request, user)

        # Редирект на страницу конкретного сервиса
        return redirect(reverse('services:service_detail', kwargs={'pk': service.pk}))


class UserLoginView(FormView):
    form_class = UserLoginForm
    template_name = 'account/login.html'

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)

        if user.is_service:
            try:
                service = AutoService.objects.get(user=user)
                return redirect('services:service_detail', pk=service.pk)
            except AutoService.DoesNotExist:
                return redirect('home')  # или другая страница если автосервис не найден

        return redirect('home')

