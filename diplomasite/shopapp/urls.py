from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ProductViewSet, ProductDetailView, PopularProductViewSet, LimitedProductViewSet, \
    TagsViewSet, BasketView, CategoriesView, CurrentUser, ReviewsProductViewSet

app_name = "shopapp"
router = DefaultRouter()
router.register(r"product", ProductViewSet, basename='product')
router.register(r'products/popular', PopularProductViewSet, basename='products-popular')
router.register(r'products/limited', LimitedProductViewSet, basename='products-limited')
router.register(r'catalog', ProductViewSet, basename='catalog')
router.register(r"tags", TagsViewSet, basename='tags')
urlpatterns = [
    path('', include(router.urls)),
    path('current_user', CurrentUser.as_view(),),
    path('product/<int:id>/reviews', ReviewsProductViewSet.as_view(),),
    path('basket', BasketView.as_view(), name='basket'),
    path('categories', CategoriesView.as_view(), name='categories'),
]
