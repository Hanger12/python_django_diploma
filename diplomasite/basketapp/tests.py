from django.test import TestCase

from django.urls import reverse
from rest_framework.test import APIClient
from shopapp.models import Product, Category
from basketapp.models import Cart, CartItem
from django.contrib.auth.models import User


class BasketViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.category1 = Category.objects.create(title="Категория 1")
        self.category2 = Category.objects.create(title="Подкатегория", parent=self.category1)
        self.product = Product.objects.create(title="Продукт 1", price=100, category=self.category2, count_in_stock=20)

    def test_get_basket_authenticated_user(self):
        """Тест GET для авторизованного пользователя"""
        self.client.force_authenticate(user=self.user)
        cart = Cart.objects.create(user=self.user)
        cart_item = CartItem.objects.create(cart=cart, product=self.product, count=3)
        response = self.client.get(reverse('basketapp:basket'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['count'], 3)

    def test_get_basket_anonymous_user(self):
        """Тест GET для неавторизованного пользователя"""
        session = self.client.session
        session['cart'] = {str(self.product.id): {'quantity': 2}}
        session.save()

        response = self.client.get(reverse('basketapp:basket'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['count'], 2)

    def test_post_basket_authenticated_user(self):
        """Тест POST для авторизованного пользователя"""
        self.client.force_authenticate(user=self.user)
        data = {'id': self.product.id, 'count': 2}

        response = self.client.post(reverse('basketapp:basket'), data)
        self.assertEqual(response.status_code, 200)
        cart = Cart.objects.get(user=self.user)
        cart_item = CartItem.objects.get(cart=cart, product=self.product)
        self.assertEqual(cart_item.count, 2)

    def test_post_basket_anonymous_user(self):
        """Тест POST для неавторизованного пользователя"""
        data = {'id': self.product.id, 'count': 1}

        response = self.client.post(reverse('basketapp:basket'), data)
        self.assertEqual(response.status_code, 200)
        session = self.client.session
        self.assertEqual(session['cart'][str(self.product.id)]['quantity'], 1)

    def test_delete_basket_authenticated_user(self):
        """Тест DELETE для авторизованного пользователя"""
        self.client.force_authenticate(user=self.user)
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, count=2)
        data = {'id': self.product.id, 'count': 1}

        response = self.client.delete(reverse('basketapp:basket'), data)
        self.assertEqual(response.status_code, 200)
        cart_item = CartItem.objects.get(cart=cart, product=self.product)
        self.assertEqual(cart_item.count, 1)

    def test_delete_basket_anonymous_user(self):
        """Тест DELETE для неавторизованного пользователя"""
        session = self.client.session
        session['cart'] = {str(self.product.id): {'quantity': 3}}
        session.save()
        data = {'id': self.product.id, 'count': 2}

        response = self.client.delete(reverse('basketapp:basket'), data)
        self.assertEqual(response.status_code, 200)
        session = self.client.session
        self.assertEqual(session['cart'][str(self.product.id)]['quantity'], 1)
