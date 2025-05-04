from rest_framework import serializers
from django.contrib.auth import get_user_model
from repairs.models import RepairRequest, RepairResponse

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_service']

class RepairRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairRequest
        fields = '__all__'

class ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairResponse
        fields = '__all__'
