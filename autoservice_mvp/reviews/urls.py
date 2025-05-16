# reviews/urls.py
from django.urls import path
from .views import CreateReviewView

app_name = 'reviews'

urlpatterns = [
    path('create/<int:service_id>/', CreateReviewView.as_view(), name='create_review'),
]
