from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from taggit.models import Tag

from .filters import ProductFilter
from .models import Product
from .serializers import ProductSerializer, TagSerializer


class ProductPagination(PageNumberPagination):
    page_size = 20

    def get_paginated_response(self, data):
        return Response({
            'items': data,
            'currentPage': self.page.number,
            'lastPage': self.page.paginator.num_pages
        })


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.prefetch_related("images").all()
    serializer_class = ProductSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    filterset_class = ProductFilter
    pagination_class = ProductPagination
    search_fields = ["title", "description"]
    ordering_fields = [
        "price",
        "date",
    ]

    def get_queryset(self):
        queryset = super().get_queryset()
        sort_type = self.request.query_params.get("sortType")
        sort_field = self.request.query_params.get("sort")

        if sort_type == 'dec':
            queryset = queryset.order_by(f'{sort_field}')
        elif sort_type == 'inc':
            queryset = queryset.order_by(f'-{sort_field}')
        return queryset


class ProductDetailView(APIView):
    def get(self, request, pk, format=None):
        product = Product.objects.get(pk=pk)
        serializer = ProductSerializer(product)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CatalogView(APIView):
    def get(self, request: Request, format=None):
        print(request.query_params)
        data = {
            "items": [
                {
                    "id": 123,
                    "category": 55,
                    "price": 500.67,
                    "count": 12,
                    "date": "Thu Feb 09 2023 21:39:52 GMT+0100 (Central European Standard Time)",
                    "title": "video card",
                    "description": "description of the product",
                    "freeDelivery": True,
                    "images": [
                        {
                            "src": "/3.png",
                            "alt": "Image alt string"
                        }
                    ],
                    "tags": [
                        {
                            "id": 12,
                            "name": "Gaming"
                        }
                    ],
                    "reviews": 5,
                    "rating": 4.6
                }
            ],
            "currentPage": 5,
            "lastPage": 10
        }
        return Response(data, status=status.HTTP_200_OK)


class PopularProductViewSet(ModelViewSet):
    queryset = Product.objects.prefetch_related("images").all()
    pagination_class = None
    serializer_class = ProductSerializer


class LimitedProductViewSet(ModelViewSet):
    queryset = Product.objects.prefetch_related("images").all()
    pagination_class = None
    serializer_class = ProductSerializer


class TagsViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    pagination_class = None
    serializer_class = TagSerializer
