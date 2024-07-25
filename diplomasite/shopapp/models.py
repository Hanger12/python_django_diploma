from django.db import models


def product_preview_directory_path(instance: "Product", filename: str):
    return "products/product_{id_product}/preview/{filename}".format(id_product=instance.pk, filename=filename)


class Product(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(null=False, blank=True)
    price = models.DecimalField(default=0, decimal_places=2)
    preview = models.ImageField(null=True, blank=True, upload_to=product_preview_directory_path)


class Reviews(models.Model):
    review = models.TextField(max_length=300, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product")
