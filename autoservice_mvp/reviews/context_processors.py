from repairs.models import RepairRequest, RepairResponse


def reviews_context(request):
    context = {
        'can_leave_review': False,
        'completed_request': None
    }

    if request.user.is_authenticated and hasattr(request, 'service'):
        # Ищем завершенную заявку, которую подтвердил этот сервис
        completed_request = RepairRequest.objects.filter(
            user=request.user,
            responses__service=request.service,
            responses__is_accepted=True,
            status='completed'
        ).exclude(
            review__isnull=False  # Исключаем заявки с уже оставленным отзывом
        ).first()

        context.update({
            'can_leave_review': completed_request is not None,
            'completed_request': completed_request
        })

    return context