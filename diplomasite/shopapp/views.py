from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from taggit.models import Tag

from .filters import ProductFilter, CustomProductSearchFilter
from .models import Product, Category, Reviews
from .serializers import ProductSerializer, TagSerializer, CategorySerializer, ReviewsSerializer


class ProductPagination(PageNumberPagination):
    page_size = 20

    def get_page_number(self, request, paginator: Paginator):
        page_number = request.query_params.get("currentPage")
        return page_number

    def get_paginated_response(self, data):
        return Response({
            'items': data,
            'currentPage': self.page.number,
            'lastPage': self.page.paginator.num_pages
        })


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        CustomProductSearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    filterset_class = ProductFilter
    pagination_class = ProductPagination
    search_fields = ["title", "description", "category__title"]
    ordering_fields = [
        "price",
        "date",
        "review_count",
    ]

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(review_count=Count('reviews'))
        category_id = self.request.query_params.get("category")
        if category_id:
            category_ids = self.get_all_category_ids(category_id)
            queryset = queryset.filter(category_id__in=category_ids)

        sort_type = self.request.query_params.get("sortType")
        sort_field = self.request.query_params.get("sort")
        sort_field = "review_count" if sort_field == "reviews" else sort_field
        if sort_type == 'dec':
            queryset = queryset.order_by(f'{sort_field}')
        elif sort_type == 'inc':
            queryset = queryset.order_by(f'-{sort_field}')
        return queryset

    def get_all_category_ids(self, category):
        # Собираем все категории и подкатегории
        category = Category.objects.prefetch_related('subcategories').get(id=category)
        categories = [category.id]

        def collect_subcategories(category):
            subcategories = category.subcategories.all()
            if subcategories:
                for subcategory in subcategories:
                    categories.append(subcategory.id)
                    collect_subcategories(subcategory)

        collect_subcategories(category)
        return categories

    def get_url(self):
        pass


class CurrentUser(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'username': request.user.username, 'email': request.user.email}, status=status.HTTP_200_OK)


class ReviewsProductViewSet(APIView):
    def post(self, request, id):
        Reviews.objects.get_or_create(product_id=int(id),
                                      author=request.user,
                                      text=request.data['text'],
                                      rate=int(request.data['rate']))
        reviews = Reviews.objects.filter(product_id=int(id))
        return Response(ReviewsSerializer(reviews, many=True, read_only=True).data, status=status.HTTP_200_OK)


class BasketView(APIView):
    def get(self, request: Request, format=None):
        data = [
            {
                "id": 123,
                "category": 55,
                "price": 500,
                "count": 1,
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
        ]
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request: Request, format=None):
        print(request.data)
        return Response(status=status.HTTP_200_OK)


class CategoriesView(APIView):
    def get(self, request: Request):
        categories = Category.objects.filter(parent__isnull=True)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
