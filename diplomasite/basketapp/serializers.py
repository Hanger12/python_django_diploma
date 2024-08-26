from rest_framework import serializers

from basketapp.models import Cart, CartItem
from shopapp.models import Product
from shopapp.serializers import ImagesProductSerializer


class ProductItemCartSerializer(serializers.ModelSerializer):
    images = ImagesProductSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'category', 'price', 'title', 'images']


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductItemCartSerializer()

    class Meta:
        model = CartItem
        fields = ['product', 'count']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Переместите `count` внутрь `product`
        product_data = representation.pop('product')
        product_data['count'] = representation['count']
        return product_data


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['user', 'items']

        def to_representation(self, instance):
            representation = super().to_representation(instance)
            return representation.pop('product') if 'product' in representation else representation
