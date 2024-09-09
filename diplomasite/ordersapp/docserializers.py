from rest_framework import serializers


class OrderIDDocSerializer(serializers.Serializer):
    orderId = serializers.IntegerField()


class ImageDocSerializer(serializers.Serializer):
    src = serializers.CharField()
    alt = serializers.CharField()


class TagDocSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class ProductDocSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    category = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    count = serializers.IntegerField()
    date = serializers.DateTimeField()
    title = serializers.CharField()
    description = serializers.CharField()
    freeDelivery = serializers.BooleanField()
    images = ImageDocSerializer(many=True)
    tags = TagDocSerializer(many=True)
    reviews = serializers.IntegerField()
    rating = serializers.FloatField()


class OrderDocSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    createdAt = serializers.DateTimeField()
    fullName = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField()
    deliveryType = serializers.CharField()
    paymentType = serializers.CharField()
    totalCost = serializers.DecimalField(max_digits=10, decimal_places=2)
    status = serializers.CharField()
    city = serializers.CharField()
    address = serializers.CharField()
    products = ProductDocSerializer(many=True)
