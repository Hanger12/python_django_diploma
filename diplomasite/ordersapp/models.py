from django.contrib.auth.models import User
from django.db import models
from accountapp.models import Profile
from shopapp.models import Product


class Order(models.Model):
    DELIVERY_CHOICES = [
        ('free', 'Free Delivery'),
        ('paid', 'Paid Delivery')
    ]

    PAYMENT_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline')
    ]

    STATUS_CHOICES = [
        ('accepted', 'Accepted'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]

    createdAt = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    deliveryType = models.CharField(max_length=10, choices=DELIVERY_CHOICES, default='free')
    paymentType = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='online')
    totalCost = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='accepted')
    city = models.CharField(max_length=30, null=False, blank=True)
    address = models.TextField(null=False, blank=True)
    products = models.ManyToManyField(Product, related_name='orders')

    def __str__(self):
        return f"Order {self.id}"
