import random

from django.http import HttpResponseRedirect
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from accountapp.serializers import ProfileSerializer, UserSerializer
from basketapp.serializers import CartSerializer, ProductItemCartSerializer, CartItemSerializer
from ordersapp.models import Order, DeliverySettings, OrderItem
from ordersapp.serializers import OrderSerializer, DeliverySettingsSerializer, OrderItemSerializer
from shopapp.models import Product
from shopapp.serializers import ProductSerializer


class OrdersView(APIView):
    def get(self, request):
        queryset = Order.objects.filter(user=request.user)
        serializer_class = OrderSerializer(queryset, many=True)
        print(serializer_class.data)
        return Response(serializer_class.data, status=status.HTTP_200_OK)

    def post(self, request):
        if request.user.is_authenticated:
            print(request.data)
            products_ids = []
            order = Order.objects.create(user=request.user)
            for data in request.data:
                product_id = data.pop('id')
                count = data.get('count')
                product = Product.objects.get(id=product_id)
                OrderItem.objects.create(order=order, product=product, count=count)
            return Response({"orderId": order.pk}, status=status.HTTP_201_CREATED)


class DeliverySettingsViewSet(ModelViewSet):
    queryset = DeliverySettings.objects.all()
    serializer_class = DeliverySettingsSerializer


class OrderView(APIView):
    def get(self, request, id):
        order = Order.objects.get(id=id)
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, id):
        order = Order.objects.get(id=id)
        order_ser = OrderSerializer(instance=order, data=request.data, partial=True)
        print(request.data)
        if order_ser.is_valid():
            order_ser.save()
        return Response(request.data, status=status.HTTP_200_OK)


class PayMentView(APIView):
    def get(self, request, id):
        return Response(status=status.HTTP_200_OK)

    def post(self, request, id):
        order = Order.objects.get(id=id).only('id')
        number = request.data['number']
        if int(number) % 2 == 0 and not number.endswith('0'):
            order_items = OrderItem.objects.filter(order=order).prefetch_related('products')
            for item in order_items:
                item.product.count += item.count
                item.product.save()
            order.status = "accepted"
            order.paymentError = 'undefined'
        else:
            order.status = 'Failed'
            order.paymentError = f"Ошибка: {random.choice(["Ошибка сети", "Проблемы с картой", "Неизвестная ошибка"])}"
        order.save()
        return Response(status=status.HTTP_200_OK)

