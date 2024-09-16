# Generated by Django 5.0.7 on 2024-09-01 18:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('shopapp', '0007_remove_product_rating'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliverySettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('express_delivery_cost', models.DecimalField(decimal_places=2, default=500.0, max_digits=10)),
                ('free_delivery_threshold', models.DecimalField(decimal_places=2, default=2000.0, max_digits=10)),
                ('standard_delivery_cost', models.DecimalField(decimal_places=2, default=200.0, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
                ('deliveryType', models.CharField(choices=[('ordinary', 'Paid Delivery'), ('express', 'Express Delivery')], default='ordinary', max_length=10)),
                ('paymentType', models.CharField(choices=[('online', 'Online'), ('someone', 'Someone')], default='online', max_length=10)),
                ('totalCost', models.DecimalField(decimal_places=2, default=0.0, max_digits=8)),
                ('status', models.CharField(choices=[('accepted', 'Accepted'), ('awaiting payment', 'Awaiting Payment'), ('completed', 'Completed'), ('Failed', 'Cancelled')], default='awaiting payment', max_length=20)),
                ('city', models.CharField(blank=True, max_length=30)),
                ('address', models.TextField(blank=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.PositiveIntegerField(default=1)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='ordersapp.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shopapp.product')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='products',
            field=models.ManyToManyField(related_name='orders', through='ordersapp.OrderItem', to='shopapp.product'),
        ),
    ]
