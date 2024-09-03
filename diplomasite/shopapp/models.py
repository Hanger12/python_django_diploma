from django.contrib.auth.models import User
from django.db import models
from taggit.managers import TaggableManager


def product_images_directory_path(instance, filename: str):
    return "products/product_{id_product}/images/{filename}".format(id_product=instance.product.pk, filename=filename)


def categories_image_directory_path(instance, filename: str):
    return "categories/category_{id}/{filename}".format(id=instance.pk, filename=filename)


class Category(models.Model):
    title = models.CharField(max_length=100, db_index=True)
    image = models.ImageField(null=True, blank=True, upload_to=categories_image_directory_path)
    parent = models.ForeignKey('self',
                               on_delete=models.CASCADE,
                               related_name='subcategories',
                               blank=True,
                               null=True)

    def __str__(self):
        return self.title


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    title = models.CharField(max_length=100, db_index=True)
    description = models.TextField(null=False, blank=True, db_index=True)
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    count = models.IntegerField()
    freeDelivery = models.BooleanField(default=False)
    available = models.BooleanField(default=True)

    tags = TaggableManager()

    def __str__(self):
        return f"{self.title}"

    # def save(self, *args, **kwargs):
    #     # Если количество товара равно 0, устанавливаем доступность как False
    #     if self.count == 0:
    #         self.available = False
    #     else:
    #         self.available = True
    #     super().save(*args, **kwargs)


class Reviews(models.Model):
    text = models.TextField(max_length=300, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    date = models.DateTimeField(auto_now_add=True)
    rate = models.IntegerField()


class Specification(models.Model):
    product = models.ManyToManyField(Product, related_name='specifications')
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}, {self.value}"


class ImagesProduct(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(null=True, blank=True, upload_to=product_images_directory_path)
