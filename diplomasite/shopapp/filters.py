from urllib.parse import urlparse, parse_qs

import django_filters
from django import forms
from django.db.models import Q
from rest_framework.filters import BaseFilterBackend
from taggit.models import Tag

from .models import Product


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='title', lookup_expr='icontains')
    minPrice = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    maxPrice = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    freeDelivery = django_filters.BooleanFilter(field_name='freeDelivery')
    available = django_filters.BooleanFilter(field_name='available')
    reviews = django_filters.NumberFilter(field_name='review_count')
    tags = django_filters.ModelMultipleChoiceFilter(field_name='tags',
                                                    queryset=Tag.objects.all(),)

    class Meta:
        model = Product
        fields = ['name', 'minPrice', 'maxPrice', 'freeDelivery', 'available', 'reviews', 'tags']

    def __init__(self, *args, **kwargs):
        # Получаем параметры запроса
        params = kwargs.get('data', {})

        # Преобразуем параметры вида filter[name] в name
        new_params = {}
        tags = []
        for key, value in params.items():
            if key.startswith('filter[') and key.endswith(']'):
                new_key = key[7:-1]  # Удаляем 'filter[' и ']'

                if value == 'false':
                    value = ''
                new_params[new_key] = value
            elif key == 'tags[]':
                tags.append(value)
            else:
                new_params[key] = value
        new_params['tags'] = tags
        kwargs['data'] = new_params
        super().__init__(*args, **kwargs)


class CustomProductSearchFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        search = request.META.get('HTTP_REFERER', '')
        parsed_url = urlparse(search)
        query_params = parse_qs(parsed_url.query)
        filter_value = query_params.get('filter', [None])[0]
        if filter_value:
            queryset = queryset.filter(
                Q(title__icontains=filter_value) |
                Q(description__icontains=filter_value) |
                Q(category__title__icontains=filter_value)
            )
        return queryset
