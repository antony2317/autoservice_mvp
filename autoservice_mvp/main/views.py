from django.shortcuts import render
from django.db.models import Q
from account.models import AutoService

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
