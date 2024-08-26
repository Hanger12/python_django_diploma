from django.http import HttpResponseRedirect
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from accountapp.serializers import ProfileSerializer, UserSerializer
from basketapp.serializers import CartSerializer
from ordersapp.models import Order
from ordersapp.serializers import OrderSerializer


class OrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'Пользователь не аутентифицирован'}, status=status.HTTP_401_UNAUTHORIZED)
        print(request.data)
        return Response({
            "orderId": 123,
        }, status=status.HTTP_200_OK)

    def get(self, request):
        data = [{
            "id": 17,
            "createdAt": "2023-05-05 12:12",
            "fullName": "Annoying Orange",
            "email": "no-reply@mail.ru",
            "phone": "88002000600",
            "deliveryType": "free",
            "paymentType": "online",
            "totalCost": 567.8,
            "status": "accepted",
            "city": "Moscow",
            "address": "red square 1",
            "products": [
                {
                    "id": 123,
                    "category": 55,
                    "price": 500.67,
                    "count": 12,
                    "date": "Thu Feb 09 2023 21:39:52 GMT+0100 (Central European Standard Time)",
                    "title": "video card",
                    "description": "description of the product",
                    "freeDelivery": True,
                    "images": [
                        {
                            "src": "/3.png",
                            "alt": "Image alt string"
                        }
                    ],
                    "tags": [
                        {
                            "id": 12,
                            "name": "Gaming"
                        }
                    ],
                    "reviews": 5,
                    "rating": 4.6
                }
            ]
        }]
        return Response(data, status=status.HTTP_200_OK)


class OrdersViewSet(ModelViewSet):
    queryset = Order.objects.all()
    # serializer_class = OrderSerializer

    # permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            print(request.data)
            products = []
            for product in request.data:
                count = product.pop('count')
                data_products = {
                    'product': product,
                    'count': count
                }
                products.append(data_products)
            data = {
                'user': request.user.pk}
            # print(user_ser.data)
            order = None
            serializer = OrderSerializer(data=data)
            if serializer.is_valid():
                order = serializer.save()
            print(serializer.errors)
            # if serializer.is_valid():
            #     pass
            # print(serializer.errors)
            # serializer.save()
            # order = Order.objects.create(user=user)
            # order = Order.objects.create(user=user)
            # serializer = self.get_serializer(order)
            # print(serializer.data)
            # if serializer.is_valid(raise_exception=True):
            #     serializer.save()
            # print(serializer.errors)
            # Создание заказа и связанных позиций заказа
            # order = serializer.save()
            return Response({"orderId": order.pk if order else 1}, status=status.HTTP_201_CREATED)

