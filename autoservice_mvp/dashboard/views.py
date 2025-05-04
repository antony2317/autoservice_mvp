from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.db.models.functions import TruncMonth
from django.db.models import Count
from django.utils.dateparse import parse_date
from repairs.models import RepairRequest, RepairResponse
from account.models import AutoService
import xlwt
from django.http import HttpResponse

import datetime

User = get_user_model()

def admin_dashboard(request):
    users = User.objects.filter(is_staff=False)
    services = User.objects.filter(is_service=True)
    repair_requests = RepairRequest.objects.all()
    responses = RepairResponse.objects.all()

    context = {
        'user_count': users.count(),
        'service_count': services.count(),
        'request_count': repair_requests.count(),
        'response_count': responses.count(),
        'users': users,
        'services': services,
        'repair_requests': repair_requests,
        'responses': responses,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)



def export_excel(request):
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")

    queryset = RepairRequest.objects.all()
    if date_from:
        queryset = queryset.filter(created_at__gte=parse_date(date_from))
    if date_to:
        queryset = queryset.filter(created_at__lte=parse_date(date_to) + datetime.timedelta(days=1))

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="repair_requests.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Заявки')

    row_num = 0
    columns = ['ID', 'Пользователь', 'Автомобиль', 'Описание', 'Статус', 'Дата создания']
    for col_num, column in enumerate(columns):
        ws.write(row_num, col_num, column)

    for req in queryset:
        row_num += 1
        ws.write(row_num, 0, req.id)
        ws.write(row_num, 1, str(req.user))
        ws.write(row_num, 2, str(req.car))
        ws.write(row_num, 3, req.description)
        ws.write(row_num, 4, req.get_status_display())
        ws.write(row_num, 5, req.created_at.strftime("%Y-%m-%d %H:%M"))

    wb.save(response)
    return response
