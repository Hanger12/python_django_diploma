from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from accountapp.models import Profile


class UserAccountTestCase(TestCase):
    def setUp(self):
        self.username = 'testuser'
        self.password = 'testpassword123'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.profile = Profile.objects.create(user=self.user)
        self.client = APIClient()

    def user_sign_in_success(self):
        url = reverse('accountapp:sign-in')
        data = {
            'username': self.username,
            'password': self.password
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get("User"))

    def test_user_sign_in_failure(self):
        url = reverse('accountapp:sign-in')
        data = {
            'username': self.username,
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_sign_up(self):
        # Тест регистрации нового пользователя
        url = reverse('accountapp:sign-up')
        data = {
            "name": "New User",
            "username": "newuser",
            "password": "newpassword123"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_sign_out(self):
        # Тест выхода пользователя
        self.client.force_authenticate(user=self.user)
        url = reverse('accountapp:sign-out')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_profile_get(self):
        # Тест получения профиля
        self.client.force_authenticate(user=self.user)
        url = reverse('accountapp:profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_profile_update(self):
        # Тест обновления профиля
        self.client.force_authenticate(user=self.user)
        url = reverse('accountapp:profile')
        data = {
            'fullName': "Новое Имя",
            'phone': "12345678901",
            'avatar': None,
            'email': "newemail@example.com"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_update_password(self):
        # Тест обновления пароля
        self.client.force_authenticate(user=self.user)
        url = reverse('accountapp:update_password')
        data = {
            'currentPassword': self.password,
            'newPassword': 'newpassword123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
