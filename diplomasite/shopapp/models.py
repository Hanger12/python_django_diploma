from django.contrib.auth.models import User
from django.db import models
from taggit.managers import TaggableManager


def product_images_directory_path(instance, filename: str):
    return "products/product_{id_product}/images/{filename}".format(id_product=instance.product.pk, filename=filename)


class Product(models.Model):
    category = models.IntegerField()
    title = models.CharField(max_length=100, db_index=True)
    description = models.TextField(null=False, blank=True, db_index=True)
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    count = models.IntegerField()
    freeDelivery = models.BooleanField(default=False)
    available = models.BooleanField(default=True)
    tags = TaggableManager()
    rating = models.FloatField()


class Reviews(models.Model):
    text = models.TextField(max_length=300, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    date = models.DateTimeField(auto_now_add=True)
    rate = models.IntegerField()


class Specification(models.Model):
    product = models.ForeignKey(Product, related_name='specifications', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)


class ImagesProduct(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(null=True, blank=True, upload_to=product_images_directory_path)
