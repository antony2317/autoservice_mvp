from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, CreateView, DetailView, DeleteView, UpdateView, TemplateView
from django.urls import reverse_lazy, reverse
from .models import Car, ServiceRecord, Garage
from .forms import CarForm, ServiceRecordForm
from django.http import JsonResponse
from .constants import CAR_MODELS
from repairs.models import RepairRequest
from account.decorators import role_required
from account.mixins import RoleRequiredMixin



def garage_search(request):
    search = request.GET.get('search', '')
    garages = Garage.objects.filter(name__icontains=search)[:10]
    data = [{'name': g.name} for g in garages]
    return JsonResponse(data, safe=False)


class GarageView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    allowed_roles = ['customer']
    model = Car
    template_name = 'garage/list.html'
    context_object_name = 'cars'

    def get_queryset(self):
        """Возвращаем только автомобили текущего пользователя"""
        return Car.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        """Добавляем заявки в контекст"""
        context = super().get_context_data(**kwargs)

        context['repair_requests'] = RepairRequest.objects.filter(
            user=self.request.user
        ).select_related('car').order_by('-created_at')[:5]

        return context





@role_required(['customer'])
def add_car(request):
    if request.method == 'POST':
        form = CarForm(request.POST)
        if form.is_valid():
            car = form.save(commit=False)
            car.user = request.user
            car.save()
            return redirect('garage')
    else:
        form = CarForm()
    return render(request, 'garage/add_car.html', {'form': form})

@role_required(['customer'])
def get_models(request):
    brand = request.GET.get('brand')
    models = CAR_MODELS.get(brand, [])
    return JsonResponse(models, safe=False)


class CarDetailView(RoleRequiredMixin, DetailView):
    allowed_roles = ['customer']
    model = Car
    template_name = 'garage/car_detail.html'
    context_object_name = 'car'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service_history'] = ServiceRecord.objects.filter(car=self.object).order_by('-date')

        # Получаем последнюю заявку
        last_request = RepairRequest.objects.filter(car=self.object).order_by('-created_at').first()

        repair_cost = None
        if last_request:
            # Ищем принятый ответ для этой заявки
            accepted_response = last_request.responses.filter(is_accepted=True).first()
            if accepted_response:
                repair_cost = accepted_response.proposed_price

        context['repair_cost'] = repair_cost
        return context



class AddServiceRecordView(RoleRequiredMixin, CreateView):
    allowed_roles = ['customer']
    model = ServiceRecord
    form_class = ServiceRecordForm
    template_name = 'garage/add_service_record.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context

    def form_valid(self, form):
        form.instance.car_id = self.kwargs['pk']
        autoservice = getattr(self.request.user, 'autoservice', None)
        form.instance.autoservice = autoservice
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('car_detail', kwargs={'pk': self.kwargs['pk']})


class EditServiceRecordView(RoleRequiredMixin, UpdateView):
    allowed_roles = ['customer']
    model = ServiceRecord
    form_class = ServiceRecordForm
    template_name = 'garage/edit_service_record.html'

    def get_success_url(self):
        return reverse('car_detail', kwargs={'pk': self.object.car.id})


class DeleteServiceRecordView(RoleRequiredMixin, DeleteView):
    allowed_roles = ['customer']
    model = ServiceRecord
    template_name = 'garage/delete_service_record.html'

    def get_success_url(self):
        return reverse('car_detail', kwargs={'pk': self.object.car.id})


class GarageDashboardView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    allowed_roles = ['customer']
    template_name = 'garage/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_staff:
            context['active_requests'] = RepairRequest.objects.filter(
                status='pending'
            ).select_related('user', 'car')
        else:
            context['user_requests'] = RepairRequest.objects.filter(
                user=self.request.user,
                status__in=['pending', 'accepted']
            ).select_related('car')

        return context