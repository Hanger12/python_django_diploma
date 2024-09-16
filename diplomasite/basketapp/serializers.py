from django.db.models import Avg
from rest_framework import serializers

from basketapp.models import Cart, CartItem
from shopapp.models import Product
from shopapp.serializers import ImagesProductSerializer, ProductSerializer, ReviewsSerializer


class ProductItemCartSerializer(serializers.ModelSerializer):
    images = ImagesProductSerializer(many=True)
    reviews = ReviewsSerializer(many=True, read_only=True, required=False)

    class Meta:
        model = Product
        fields = ['id', 'category', 'price', 'title', 'images',
                  'date', 'description', 'freeDelivery', 'reviews']

    def create(self, validated_data):
        print(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        reviews = representation.get('reviews', [])
        if isinstance(reviews, list):
            reviews_count = len(reviews)
            total_rating = sum(review.get('rate', 0) for review in reviews)
            average_rating = total_rating / reviews_count if reviews_count > 0 else None
            representation['rating'] = average_rating
        else:
            reviews_count = reviews
        representation['reviews'] = reviews_count
        return representation


class CombinedItemSerializer(serializers.ModelSerializer):
    # Assuming that 'product' is a common field in both models.
    product = ProductItemCartSerializer(read_only=True)

    class Meta:
        # Define abstract class without a model, to be inherited and specified in the derived classes
        abstract = True
        fields = ['product', 'count']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Move `count` inside `product`
        product_data = representation.pop('product', None)
        if product_data is not None:
            # If product data exists, add the count
            product_data['count'] = representation['count']
        else:
            # If product data not found, create an empty object with count
            product_data = {'count': representation['count']}
        return product_data


class CartItemSerializer(CombinedItemSerializer):
    class Meta(CombinedItemSerializer.Meta):
        model = CartItem


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['items']
