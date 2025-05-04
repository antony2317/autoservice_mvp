from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RepairRequestViewSet, RepairResponseViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'repair-requests', RepairRequestViewSet)
router.register(r'responses', RepairResponseViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
