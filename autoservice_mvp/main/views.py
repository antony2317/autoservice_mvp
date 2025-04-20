from django.shortcuts import render

def index(request):
    context = {
        'title': 'Главная страница',
        'features': [
            'Запись в сервис онлайн',
            'История обслуживания',
            'Рейтинги автосервисов',
        ]
    }
    return render(request, 'main/index.html', context)
