from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, DetailView, DeleteView, UpdateView, TemplateView
from django.urls import reverse_lazy, reverse
from .models import Car, ServiceRecord, Garage, CarBase
from .forms import CarForm, ServiceRecordForm
from django.http import JsonResponse
from .constants import CAR_MODELS
from repairs.models import RepairRequest
from account.decorators import role_required
from account.mixins import RoleRequiredMixin
from datetime import datetime
from django.db.models import Q



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
            try:
                car = form.save(commit=False)
                car.user = request.user  # ← обязательно, иначе не сохранится
                car.base_car = form.cleaned_data.get('base_car')
                car.year = int(form.cleaned_data.get('year'))

                car.save()
                messages.success(request, 'Автомобиль успешно добавлен.')
                return redirect('garage')
            except Exception as e:
                print("Ошибка при сохранении:", e)
                messages.error(request, f'Ошибка при сохранении: {e}')
        else:
            print("Ошибки формы:", form.errors)
            messages.error(request, 'Проверьте форму на ошибки.')
    else:
        form = CarForm()

    return render(request, 'garage/add_car.html', {'form': form})

@role_required(['customer'])
def get_models(request):
    brand = request.GET.get('brand')
    if not brand:
        return JsonResponse([], safe=False)

    models = (
        CarBase.objects.filter(brand=brand)
        .values_list('model', flat=True)
        .distinct()
    )
    return JsonResponse(sorted(models), safe=False)






@role_required(['customer'])
def get_years(request):
    brand = request.GET.get('brand')
    model = request.GET.get('model')
    generation = request.GET.get('generation')
    current_year = datetime.now().year

    queryset = CarBase.objects.filter(brand=brand, model=model)
    if generation:
        queryset = queryset.filter(generation=generation)

    years = set()
    for entry in queryset:
        end_year = entry.year_to or current_year
        years.update(range(entry.year_from, end_year + 1))

    return JsonResponse({'years': sorted(years)})


@role_required(['customer'])
def get_generation(request):
    brand = request.GET.get('brand')
    model = request.GET.get('model')
    try:
        year = int(request.GET.get('year'))
    except (TypeError, ValueError):
        return JsonResponse({'generation': ''})

    current_year = datetime.now().year

    try:
        car_base = CarBase.objects.filter(
            brand=brand,
            model=model,
            year_from__lte=year
        ).filter(
            Q(year_to__gte=year) | Q(year_to__isnull=True)
        ).first()

        generation = car_base.generation if car_base else ''
    except CarBase.DoesNotExist:
        generation = ''

    return JsonResponse({'generation': generation or ''})


@role_required(['customer'])
def get_engine_types(request):
    brand = request.GET.get('brand')
    model = request.GET.get('model')
    year = request.GET.get('year')

    try:
        year = int(year)
    except (TypeError, ValueError):
        return JsonResponse([], safe=False)

    if not (brand and model):
        return JsonResponse([], safe=False)

    engine_types = CarBase.objects.filter(
        brand=brand,
        model=model,
        year_from__lte=year
    ).filter(
        Q(year_to__gte=year) | Q(year_to__isnull=True)
    ).values_list('engine_type', flat=True).distinct()

    ENGINE_TYPE_CHOICES = dict(CarBase._meta.get_field('engine_type').choices)

    result = [
        [etype, ENGINE_TYPE_CHOICES.get(etype, etype)]
        for etype in engine_types
    ]
    return JsonResponse(result, safe=False)


@role_required(['customer'])
def get_engine_volumes(request):
    brand = request.GET.get('brand')
    model = request.GET.get('model')
    engine_type = request.GET.get('engine_type')
    year = request.GET.get('year')

    try:
        year = int(year)
    except (TypeError, ValueError):
        return JsonResponse([], safe=False)

    if not (brand and model and engine_type):
        return JsonResponse([], safe=False)

    volumes = CarBase.objects.filter(
        brand=brand,
        model=model,
        engine_type=engine_type,
        year_from__lte=year
    ).filter(
        Q(year_to__gte=year) | Q(year_to__isnull=True)
    ).values_list('engine_volume', flat=True).distinct()

    return JsonResponse(sorted(volumes), safe=False)

class CarDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Car
    template_name = 'garage/car_confirm_delete.html'
    success_url = reverse_lazy('garage')

    def test_func(self):
        car = self.get_object()
        return car.user == self.request.user  # можно удалять только свои авто

class CarDetailView(RoleRequiredMixin, DetailView):
    allowed_roles = ['customer']
    model = Car
    template_name = 'garage/car_detail.html'
    context_object_name = 'car'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service_history'] = ServiceRecord.objects.filter(car=self.object).order_by('-date')


        last_request = RepairRequest.objects.filter(car=self.object).order_by('-created_at').first()

        repair_cost = None
        if last_request:

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

