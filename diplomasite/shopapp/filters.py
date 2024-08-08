import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='title', lookup_expr='icontains')
    minPrice = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    maxPrice = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    freeDelivery = django_filters.BooleanFilter(field_name='freeDelivery')
    available = django_filters.BooleanFilter(field_name='available')

    class Meta:
        model = Product
        fields = ['name', 'minPrice', 'maxPrice', 'freeDelivery', 'available']

    def __init__(self, *args, **kwargs):
        print(kwargs)
        # Получаем параметры запроса
        params = kwargs.get('data', {})

        # Преобразуем параметры вида filter[name] в name
        new_params = {}
        for key, value in params.items():
            if key.startswith('filter[') and key.endswith(']'):
                new_key = key[7:-1]  # Удаляем 'filter[' и ']'
                if value == 'false':
                    value = ''
                new_params[new_key] = value
            else:
                new_params[key] = value

        kwargs['data'] = new_params
        super().__init__(*args, **kwargs)
