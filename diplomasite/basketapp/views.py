from django.shortcuts import render
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from basketapp.models import Cart, CartItem
from basketapp.serializers import ProductItemCartSerializer, CartSerializer
from shopapp.models import Product
from shopapp.serializers import ProductSerializer


def get_list_session_item(cart):
    cart_items = []
    for product_id, item in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            quantity = item['quantity']
            serializer_data = ProductItemCartSerializer(product).data.copy()
            serializer_data['count'] = quantity
            cart_items.append(serializer_data)
        except Product.DoesNotExist:
            pass
    return cart_items


class BasketView(APIView):
    """Представление корзины товаров, которое обрабатывает
    добавление/удаление/обновление/вывод товаров в корзину"""

    @extend_schema(
        summary="Получить список товаров в корзине",
        description='',
        responses=CartSerializer
    )
    def get(self, request):
        """GET запрос обабатывает вывод товаров, находящиеся в корзине"""
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart_session = request.session.get('cart', {})
            if not cart_session == {}:
                for product_id, item in cart_session.items():
                    product = Product.objects.only('id').get(id=product_id)
                    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
                    if created:
                        cart_item.count = item['quantity']
                    else:
                        cart_item.count += item['quantity']
                    cart_item.save()
                request.session.pop('cart', None)
            serializer = CartSerializer(cart)
            # print(serializer.data)
            return Response(serializer.data['items'], status=status.HTTP_200_OK)
        else:
            cart = request.session.get('cart', {})
            return Response(get_list_session_item(cart), status=status.HTTP_200_OK)

    @extend_schema(
        summary="Добавить товар в корзину",
        parameters=[OpenApiParameter('product_id', int, description='ID продукта'),
                    OpenApiParameter('count', int, description='Количество товара')
                    ],
        responses=CartSerializer
    )
    def post(self, request):
        """Добавление товара в корзину"""
        product_id = str(request.data.get('id'))
        quantity = request.data.get('count')
        if not product_id or quantity is None:
            return Response({'error': 'Invalid input'}, status=status.HTTP_400_BAD_REQUEST)
        product = get_object_or_404(Product, id=product_id)
        if product.count_in_stock == 0:
            return Response({'error': 'Invalid input'}, status=status.HTTP_400_BAD_REQUEST)
        if request.user.is_authenticated:
            # Для авторизованных пользователей
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
            if not created:
                cart_item.count += int(quantity)
            else:
                cart_item.count = int(quantity)
            cart_item.save()
            serializer = CartSerializer(cart)
            return Response(serializer.data['items'], status=status.HTTP_200_OK)
        else:
            # Для неавторизованных пользователей
            cart = request.session.get('cart', {})
            print(cart)
            if product_id in cart:
                cart[product_id]['quantity'] += int(quantity)
            else:
                cart[product_id] = {'quantity': int(quantity)}
            request.session['cart'] = cart
            return Response(get_list_session_item(cart), status=status.HTTP_200_OK)

    @extend_schema(
        summary="Удалить товар из корзины",
        parameters=[OpenApiParameter('product_id', int, description='ID продукта'),
                    OpenApiParameter('count', int, description='Количество товара')
                    ],
        responses=CartSerializer()
    )
    def delete(self, request: Request):
        """Удаление товаров из корзины"""
        product_id = str(request.data.get('id'))
        quantity = request.data.get('count')
        if request.user.is_authenticated:
            # Для авторизованных пользователей
            cart = get_object_or_404(Cart, user=request.user)
            product = get_object_or_404(Product, id=product_id)
            cart_item = CartItem.objects.get(cart=cart, product=product)
            if cart_item.count <= int(quantity):
                cart_item.delete()
            else:
                cart_item.count -= int(quantity)
                cart_item.save()
            serializer = CartSerializer(cart)
            return Response(serializer.data['items'], status=status.HTTP_200_OK)
        else:
            # Для неавторизованных пользователей
            cart = request.session.get('cart', {})
            if product_id in cart:
                item = cart[product_id]
                if item['quantity'] <= int(quantity):
                    del cart[product_id]
                else:
                    cart[product_id]['quantity'] -= int(quantity)
                request.session['cart'] = cart
                return Response(get_list_session_item(cart), status=status.HTTP_200_OK)
