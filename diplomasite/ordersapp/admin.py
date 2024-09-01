from django.contrib import admin

from ordersapp.models import DeliverySettings


@admin.register(DeliverySettings)
class DeliverySettingsAdmin(admin.ModelAdmin):
    list_display = ('express_delivery_cost', 'free_delivery_threshold', 'standard_delivery_cost')
