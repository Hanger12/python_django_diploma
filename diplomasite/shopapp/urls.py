from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ProductViewSet, ProductDetailView, PopularProductViewSet, CatalogView, LimitedProductViewSet, \
    TagsViewSet

app_name = "shopapp"
router = DefaultRouter()
router.register(r"product", ProductViewSet, basename='product')
router.register(r'products/popular', PopularProductViewSet, basename='products-popular')
router.register(r'products/limited', LimitedProductViewSet, basename='products-limited')
router.register(r'catalog', ProductViewSet, basename='catalog')
router.register(r"tags", TagsViewSet, basename='tags')
urlpatterns = [
    path('', include(router.urls)),
    # path('catalog/', CatalogView.as_view(), name='catalog')
]
