from django.contrib import messages
from django.shortcuts import redirect, JsonResponse
from django.urls import resolve
from django.conf import settings
from django.core.exceptions import PermissionDenied


class RoleAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        # URL, доступные всем (включая неавторизованных)
        PUBLIC_URLS = [
            'home',
            'login',
            'logout',
            'signup',

        ]

        # Полные правила доступа для URL
        ACCESS_RULES = {
            # Чат
            'chat_between_users': ['customer', 'service'],
            'fetch_messages': ['customer', 'service'],
            'chat_with_service': ['customer', 'service'],

            # Админка и управление
            'dashboard': ['admin', 'manager'],
            'admin_users': ['admin', 'manager'],
            'block_user': ['admin', 'manager'],
            'delete_user': ['admin', 'manager'],
            'change_user_role': ['admin', 'manager'],
            'admin_services': ['admin', 'manager'],
            'block_service': ['admin', 'manager'],
            'admin_requests': ['admin', 'manager'],
            'change_request_status': ['admin', 'manager'],
            'delete_request': ['admin', 'manager'],

            # Гаражи и автомобили
            'garage': ['customer'],
            'add_car': ['customer'],
            'get_models': ['customer'],
            'car_detail': ['customer'],
            'add_service_record': ['customer'],
            'garage_search': ['customer'],
            'edit_service_record': ['customer'],
            'delete_service_record': ['customer'],
            'create_request': ['customer'],

            # Сервисы
            'service_detail': ['customer', 'service'],
            'service_dashboard': ['service'],
            'my_responses': ['service'],
            'service_profile': ['service'],
            'my_services': ['service'],
            'add_service': ['service'],
            'edit_service': ['service'],
            'delete_service': ['service'],
            'accepted_requests': ['service'],

            # Обработка откликов
            'respond_to_request': ['service'],
            'confirm_response': ['customer'],
            'accept_response': ['customer'],

            # API endpoints
            'api:respond_to_request': ['service'],
            'api:confirm_response': ['customer'],
        }

        # Пропускаем OPTIONS запросы (для CORS)
        if request.method == 'OPTIONS':
            return None

        # Проверка доступа к админке Django
        if request.path.startswith('/admin/'):
            if not request.user.is_authenticated:
                return redirect(f'{settings.LOGIN_URL}?next={request.path}')
            if not hasattr(request.user, 'role') or request.user.role != 'admin':
                raise PermissionDenied("Доступ в админку разрешен только администраторам")
            return None

        # Пропускаем статические файлы и медиа
        if request.path.startswith(settings.STATIC_URL) or request.path.startswith(settings.MEDIA_URL):
            return None

        # Получаем имя URL
        try:
            resolved = resolve(request.path_info)
            url_name = resolved.url_name
            # Для DRF и API добавляем namespace
            if hasattr(resolved, 'namespace') and resolved.namespace:
                url_name = f"{resolved.namespace}:{url_name}"
        except:
            return None  # если URL не существует (404)

        # Публичные URL
        if url_name in PUBLIC_URLS:
            return None

        # Проверка авторизации
        if not request.user.is_authenticated:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Требуется авторизация'}, status=401)
            return redirect(settings.LOGIN_URL)

        # Проверка ролей для AJAX/API запросов
        if (request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
                request.content_type == 'application/json'):

            if url_name in ACCESS_RULES:
                if request.user.role not in ACCESS_RULES[url_name]:
                    return JsonResponse(
                        {'error': 'Недостаточно прав для этого действия'},
                        status=403
                    )
            else:
                return JsonResponse(
                    {'error': 'Endpoint не найден или недоступен'},
                    status=404
                )
            return None

        # Проверка ролей для обычных запросов
        if url_name in ACCESS_RULES:
            if request.user.role not in ACCESS_RULES[url_name]:
                messages.error(request, "У вас нет доступа к этой странице")
                return redirect('home')
        else:
            messages.error(request, "Страница не найдена")
            return redirect('home')

        return None