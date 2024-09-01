from django.contrib.auth.models import User
from django.db import models
from accountapp.models import Profile
from shopapp.models import Product


class Order(models.Model):
    class DeliveryChoices(models.TextChoices):
        ORDINARY = 'ordinary', 'Paid Delivery'
        EXPRESS = 'express', 'Express Delivery'

    class PaymentChoices(models.TextChoices):
        ONLINE = 'online', 'Online'
        SOMEONE = 'someone', 'Someone'

    class StatusChoices(models.TextChoices):
        ACCEPTED = 'accepted', 'Accepted'
        AWAITING_PAYMENT = 'awaiting payment', 'Awaiting Payment'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'Failed', 'Cancelled'

    createdAt = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    deliveryType = models.CharField(max_length=10, choices=DeliveryChoices.choices, default=DeliveryChoices.ORDINARY)
    paymentType = models.CharField(max_length=10, choices=PaymentChoices.choices, default=PaymentChoices.ONLINE)
    totalCost = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.AWAITING_PAYMENT)
    city = models.CharField(max_length=30, null=False, blank=True)
    address = models.TextField(null=False, blank=True)
    products = models.ManyToManyField(Product, through='OrderItem', related_name='orders')
    paymentError = models.CharField(max_length=50, null=True)

    def __str__(self):
        return f"Order {self.id}"


class DeliverySettings(models.Model):
    express_delivery_cost = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)
    free_delivery_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=2000.00)
    standard_delivery_cost = models.DecimalField(max_digits=10, decimal_places=2, default=200.00)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=1)
