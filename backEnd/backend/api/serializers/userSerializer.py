from rest_framework import serializers
from ..models.user import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'first_name', 'last_name',
                  'role', 'is_active', 'employee_code', 'birth_date',
                  'address', 'cccd']
        extra_kwargs = {'password': {'write_only': True},}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
