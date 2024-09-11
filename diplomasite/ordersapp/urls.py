from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import OrderView, OrdersView, PayMentView, DeliverySettingsViewSet

app_name = "ordersapp"

router = DefaultRouter(trailing_slash=False)
router.register(r"delivery-settings", DeliverySettingsViewSet, basename='delivery-settings')
urlpatterns = [
    path('', include(router.urls)),
    path('order/<int:id>', OrderView.as_view(), name='order'),
    path('orders', OrdersView.as_view(), name='orders'),
    path('payment/<int:id>', PayMentView.as_view(), name='payment'),
]
