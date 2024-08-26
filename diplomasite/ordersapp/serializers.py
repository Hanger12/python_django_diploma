from rest_framework import serializers

from accountapp.models import Profile
from accountapp.serializers import ProfileSerializer, UserSerializer
from basketapp.serializers import ProductItemCartSerializer, CartItemSerializer, CartSerializer
from ordersapp.models import Order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', ]

    def create(self, validated_data):
        # products = validated_data.pop('products', [])
        user = validated_data.pop('user')
        order = Order.objects.create(user=user)
        # for product in products:
        #     serializer = ProductItemCartSerializer(product['product'])
        #     print(serializer.data)
        #     # order.products.add(product)
        print('сюда зашли')
        return order

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        user = representation.pop('user')
        profile = Profile.objects.get(user=user)
        profile = ProfileSerializer(profile).data
        profile.pop('avatar')
        return profile
