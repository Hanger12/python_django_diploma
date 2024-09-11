from django.contrib.auth.models import User
from django.test import TestCase

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accountapp.models import Profile
from basketapp.models import Cart
from shopapp.models import Product, Category
from .models import Order, OrderItem


class OrdersAppTestCase(APITestCase):

    def setUp(self):
        # Create user and login
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.profile = Profile.objects.create(user=self.user)
        self.client.login(username='testuser', password='testpass')
        self.category1 = Category.objects.create(title="Категория 1")
        self.category2 = Category.objects.create(title="Подкатегория", parent=self.category1)
        self.product1 = Product.objects.create(title="Product 1", count=100, count_in_stock=50, category=self.category2)
        self.product2 = Product.objects.create(title="Product 2", count=200, count_in_stock=100, category=self.category2)
        self.order = Order.objects.create(user=self.user)
        OrderItem.objects.create(order=self.order, product=self.product1, count=2)
        OrderItem.objects.create(order=self.order, product=self.product2, count=1)
        Cart.objects.create(user=self.user)

    def test_get_orders(self):
        url = reverse('ordersapp:orders')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_order(self):
        url = reverse('ordersapp:orders')
        data = [
            {"id": self.product1.id, "count": 1},
            {"id": self.product2.id, "count": 2}
        ]
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('orderId', response.data)

    def test_get_order_by_id(self):
        url = reverse('ordersapp:order', args=[self.order.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.order.id)

    def test_update_order(self):
        url = reverse('ordersapp:order', args=[self.order.id])
        data = {'status': 'completed'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')

    def test_payment_successful(self):
        url = reverse('ordersapp:payment', args=[self.order.id])
        data = {
            "number": "8888888888888888",
            "name": "Test User",
            "month": "02",
            "year": "2025",
            "code": "123"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'accepted')

    def test_payment_failed(self):
        url = reverse('ordersapp:payment', args=[self.order.id])
        data = {
            "number": "7777777777777777",
            "name": "Test User",
            "month": "02",
            "year": "2025",
            "code": "123"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'Failed')
