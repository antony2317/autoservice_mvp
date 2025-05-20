# reviews/views.py
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from .forms import ReviewForm
from .models import Review
from account.models import User


class CreateReviewView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'reviews/create_review.html'


    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['service'] = get_object_or_404(User, pk=self.kwargs['service_id'])
        return kwargs

    def form_valid(self, form):
        service = get_object_or_404(User, pk=self.kwargs['service_id'])
        print(f'User: {self.request.user}, Service: {service}')  # debug

        if Review.objects.filter(user=self.request.user, service=service).exists():
            messages.error(self.request, 'Вы уже оставляли отзыв для этого сервиса.')
            return redirect('services:service_detail', pk=service.pk)

        review = form.save(commit=False)
        review.user = self.request.user
        review.service = service.user

        print(f'Review before save: user={review.user}, service={review.service}, rating={review.rating}')  # debug
        review.save()
        print('Review saved')  # debug

        messages.success(self.request, 'Спасибо за отзыв!')
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, 'Ошибка. Проверьте форму.')
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('services:service_detail', kwargs={'pk': self.kwargs['service_id']})
