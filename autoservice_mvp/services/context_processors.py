from account.models import AutoService

def service_context(request):
    """
    Добавляет объект AutoService в контекст, если пользователь — автосервис.
    """
    if request.user.is_authenticated and getattr(request.user, 'is_service', False):
        try:
            service = AutoService.objects.get(user=request.user)
            return {'service': service}
        except AutoService.DoesNotExist:
            pass
    return {}
