from rest_framework import serializers

from accountapp.models import Profile
from accountapp.serializers import ProfileSerializer, UserSerializer
from basketapp.models import CartItem
from basketapp.serializers import ProductItemCartSerializer, CartItemSerializer, CartSerializer, CombinedItemSerializer
from ordersapp.models import Order, DeliverySettings, OrderItem
from shopapp.serializers import ProductSerializer


class OrderItemSerializer(CombinedItemSerializer):
    class Meta(CombinedItemSerializer.Meta):
        model = OrderItem


class OrderSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField(required=False)
    user = ProfileSerializer(source='user.profile', required=False)

    class Meta:
        model = Order
        fields = '__all__'

    def get_products(self, obj):
        order_items = OrderItem.objects.filter(order=obj)
        serializer = OrderItemSerializer(order_items, many=True)
        return serializer.data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        user = representation.pop('user')
        representation['fullName'] = user['fullName']
        representation['email'] = user['email']
        representation['phone'] = user['phone']
        return representation


class DeliverySettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliverySettings
        fields = '__all__'
