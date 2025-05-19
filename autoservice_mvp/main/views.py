from django.shortcuts import render
from django.db.models import Q
from account.models import AutoService
from django.shortcuts import render

def index(request):
    query = request.GET.get('q', '')
    services = AutoService.objects.all()
    if query:
        services = services.filter(
            Q(name__icontains=query) | Q(address__icontains=query)
        )

    context = {
        'title': 'Главная страница',
        'features': [
            'Запись в сервис онлайн',
            'История обслуживания',
            'Рейтинги автосервисов',
        ],
        'services_list': services,
        'search_query': query,
    }
    return render(request, 'main/index.html', context)




def custom_404_view(request, exception):
    return render(request, '404.html', status=404)

def custom_500_view(request):
    return render(request, '500.html', status=500)