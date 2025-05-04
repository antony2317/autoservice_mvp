from rest_framework import viewsets
from django.contrib.auth import get_user_model
from repairs.models import RepairRequest, RepairResponse
from .serializers import UserSerializer, RepairRequestSerializer, ResponseSerializer

User = get_user_model()

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class RepairRequestViewSet(viewsets.ModelViewSet):
    queryset = RepairRequest.objects.all()
    serializer_class = RepairRequestSerializer

class RepairResponseViewSet(viewsets.ModelViewSet):
    queryset = RepairResponse.objects.all()
    serializer_class = ResponseSerializer
