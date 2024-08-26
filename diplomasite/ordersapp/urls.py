from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import OrderView, OrdersViewSet

app_name = "ordersapp"

router = DefaultRouter(trailing_slash=False)
router.register(r"orders", OrdersViewSet, basename='orders')
# router.register(r'order', OrderViewSet, basename='order')
urlpatterns = [
    # path('', include(router.urls)),
    path('orders', OrderView.as_view(), name='orders')

]
