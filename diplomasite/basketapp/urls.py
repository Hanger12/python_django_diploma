from django.urls import path, include

from basketapp.views import BasketView

app_name = "basketapp"

urlpatterns = [
    path('basket', BasketView.as_view(), name='basket'),
]