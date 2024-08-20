from django.db.models import Avg
from rest_framework import serializers
from taggit.models import Tag
from taggit.serializers import TagListSerializerField

from .models import Product, ImagesProduct, Specification, Reviews, Category


class ImagesProductSerializer(serializers.ModelSerializer):
    src = serializers.CharField(source='image.url', read_only=True)
    alt = serializers.CharField(source='image.name', read_only=True)

    class Meta:
        model = ImagesProduct
        fields = ['src', 'alt']


class SpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = ['name', 'value']


class ReviewsSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()

    class Meta:
        model = Reviews
        fields = ['author', 'email', 'text', 'rate', 'date']

    def get_email(self, obj):
        return obj.author.email

    def get_author(self, obj):
        return obj.author.username


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class ProductSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    specifications = SpecificationSerializer(many=True, read_only=True)
    reviews = ReviewsSerializer(many=True, read_only=True)
    images = ImagesProductSerializer(many=True, read_only=True)
    fullDescription = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'

    def get_fullDescription(self, obj):
        return obj.description

    def get_description(self, obj):
        return obj.description[:30] + '...'

    def get_rating(self, obj):
        average_rating = obj.reviews.aggregate(average=Avg('rate'))['average']
        return round(average_rating, 2) if average_rating else 0.0


class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'title', 'image', 'subcategories']

    def get_subcategories(self, obj):
        subcategories = obj.subcategories.all()
        return CategorySerializer(subcategories, many=True).data

    def get_image(self, obj):
        return {"src": obj.image.url, "alt": obj.image.name}
