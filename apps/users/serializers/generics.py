import logging

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.users.models import CompanyUser, Company

logger = logging.getLogger(__name__)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['password', 'email']

    def create(self, validated_data):
        validated_data["username"] = validated_data["email"]
        user = User.objects.create_user(**validated_data)
        return user


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'is_active']


class CompanyUserSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = CompanyUser
        fields = ['id', 'user', 'user_id', 'company', 'role']
        extra_kwargs = {'company': {'read_only': True}}

    def validate_user_id(self, value):
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("User does not exist")
        return value

    def validate(self, attrs):
        company = self.context['company']
        user_id = attrs['user_id']

        # Check if user is already in company
        if CompanyUser.objects.filter(company=company, user_id=user_id).exists():
            raise serializers.ValidationError("User is already in this company")

        return attrs


class ChangeRoleSerializer(serializers.Serializer):
    role = serializers.IntegerField()

    def validate_role(self, value):
        if value not in dict(CompanyUser.RoleChoices.choices):
            raise serializers.ValidationError("Invalid role")
        return value
