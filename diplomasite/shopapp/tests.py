import time

from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory
from django.urls import reverse

from shopapp.models import Category, Product, Reviews
from shopapp.views import ProductViewSet


class ProductViewSetTestCase(TestCase):
    def set(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.category1 = Category.objects.create(title="Категория 1")
        self.category2 = Category.objects.create(title="Подкатегория", parent=self.category1)
        self.product1 = Product.objects.create(title="Продукт 1", price=100, category=self.category2, count_in_stock=20)
        time.sleep(2)
        self.product2 = Product.objects.create(title="Продукт 2", price=200, category=self.category2, count_in_stock=20)
        self.review1 = Reviews.objects.create(author=self.user, product=self.product1, rate=5, text="Тестовый отзыв 1")
        self.review2 = Reviews.objects.create(author=self.user, product=self.product2, rate=4, text="Тестовый отзыв 2")
        self.review3 = Reviews.objects.create(author=self.user, product=self.product2, rate=3, text="Тестовый отзыв 3")

    def test_get_products_list(self):
        request = self.factory.get('/api/catalog/', {'currentPage': 1, 'limit': 20})
        view = ProductViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['items']), 2)

    def test_products_sort(self):
        # Сортировка по цене
        request = self.factory.get('/api/catalog/',
                                   {"sort": 'price', 'sortType': 'dec', 'currentPage': 1, 'limit': 20})
        view = ProductViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['items'][0]['title'], 'Продукт 1')
        request = self.factory.get('/api/catalog/',
                                   {"sort": 'price', 'sortType': 'inc', 'currentPage': 1, 'limit': 20})
        view = ProductViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['items'][0]['title'], 'Продукт 2')

        # Сортировка по рейтингу
        request = self.factory.get('/api/catalog/',
                                   {"sort": 'rating', 'sortType': 'inc', 'currentPage': 1, 'limit': 20})
        view = ProductViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['items'][0]['title'], 'Продукт 1')
        request = self.factory.get('/api/catalog/',
                                   {"sort": 'rating', 'sortType': 'dec', 'currentPage': 1, 'limit': 20})
        view = ProductViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['items'][0]['title'], 'Продукт 2')

        # Сортировка по отзывам
        request = self.factory.get('/api/catalog/',
                                   {"sort": 'reviews', 'sortType': 'dec', 'currentPage': 1, 'limit': 20})
        view = ProductViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['items'][0]['title'], 'Продукт 1')
        request = self.factory.get('/api/catalog/',
                                   {"sort": 'reviews', 'sortType': 'inc', 'currentPage': 1, 'limit': 20})
        view = ProductViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['items'][0]['title'], 'Продукт 2')

        # Сортировка по Новизне
        request = self.factory.get('/api/catalog/',
                                   {"sort": 'date', 'sortType': 'inc', 'currentPage': 1, 'limit': 20})
        view = ProductViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['items'][0]['title'], 'Продукт 2')
        request = self.factory.get('/api/catalog/',
                                   {"sort": 'date', 'sortType': 'dec', 'currentPage': 1, 'limit': 20})
        view = ProductViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['items'][0]['title'], 'Продукт 1')

    def test_review_annotations(self):
        request = self.factory.get('/api/catalog/', {'currentPage': 1, 'limit': 20})
        view = ProductViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        product1_data = next(item for item in response.data['items'] if item['title'] == 'Продукт 1')
        product2_data = next(item for item in response.data['items'] if item['title'] == 'Продукт 2')
        self.assertEqual(len(product1_data['reviews']), 1)
        self.assertEqual(product1_data['rating'], 5.0)
        self.assertEqual(len(product2_data['reviews']), 2)
        self.assertEqual(product2_data['rating'], 3.5)

    def test_filters_product(self):
        request = self.factory.get('/api/catalog/', {'currentPage': 1, 'limit': 20,
                                                     'category': self.category2.id})
        view = ProductViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['items']), 2)
