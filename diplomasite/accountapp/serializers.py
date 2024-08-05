from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Profile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'email', 'last_name']


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    fullName = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['avatar', 'phone', 'fullName', "email"]

    def get_email(self, obj):
        return obj.user.email

    def get_avatar(self, obj):
        return obj.avatar_info

    def get_fullName(self, obj):
        return obj.fullName


class ProfileUpdateSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Profile
        fields = ['phone', 'middle_name', "user"]

    def update(self, instance, validated_data):
        user = validated_data.pop("user")
        instance.phone = validated_data.get("phone", instance.phone)
        instance.middle_name = validated_data.get("middle_name", instance.middle_name)
        instance.user.first_name = user.get("first_name")
        instance.user.last_name = user.get("last_name")
        instance.user.email = user.get("email")
        instance.user.save()
        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    currentPassword = serializers.CharField(required=True)
    newPassword = serializers.CharField(required=True)

    # def validate(self, data):
    #     user = self.context['request'].user
    #     if not user.check_password(data['currentPassword']):
    #         raise serializers.ValidationError({"currentPassword": "Неверный старый пароль"})
    #     if data['currentPassword'] == data['newPassword']:
    #         raise serializers.ValidationError({"newPassword": "Новый пароль не может быть таким же, как старый"})
    #     return data

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['newPassword'])
        user.save()
        update_session_auth_hash(self.context['request'], user)


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        print(validated_data)
        user = User(
            first_name=validated_data['first_name'],
            username=validated_data['username'],
        )
        user.set_password(validated_data['password'])
        user.save()
        Profile.objects.create(user=user)
        return user
