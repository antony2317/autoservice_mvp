from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .forms import AutoServiceProfileForm
from account.models import AutoService
from repairs.models import RepairResponse

@login_required
def service_profile(request):
    if not request.user.is_service:
        return redirect('home')


    auto_service = get_object_or_404(AutoService, user=request.user)

    if request.method == 'POST':
        form = AutoServiceProfileForm(request.POST, instance=auto_service)
        if form.is_valid():
            form.save()
            return redirect('services:service_profile')
    else:
        form = AutoServiceProfileForm(instance=auto_service)

    return render(request, 'services/service_profile.html', {'form': form, 'auto_service': auto_service})




def my_responses(request):
    all_responses = RepairResponse.objects.filter(
        service=request.user,
        is_accepted=False
    ).select_related('repair_request')


    responses = [r for r in all_responses if not r.repair_request.has_accepted_response]

    return render(request, 'services/my_responses.html', {'responses': responses})
