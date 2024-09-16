from django.core.paginator import Paginator
from django.db.models import Count, Q, Avg
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiResponse, extend_schema_view, OpenApiParameter
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


@extend_schema_view(
    list=extend_schema(
        summary="Список продуктов",
        description="Получение списка продуктов с пагинацией. Можно фильтровать и сортировать с помощью параметров "
                    "запроса.",
        parameters=[
            OpenApiParameter(name='category', description='Фильтрация по ID категории', required=False,
                             type=OpenApiTypes.INT),
            OpenApiParameter(name='sort', description='Сортировка по полю (например, price, date, reviews)',
                             required=False, type=OpenApiTypes.STR),
            OpenApiParameter(name='sortType', description='Тип сортировки: inc (возрастание) или dec (убывание)',
                             required=False, type=OpenApiTypes.STR),
        ],
    ),
    retrieve=extend_schema(
        summary="Список продуктов отфильтрованных по id",
        description="Получение списка продуктов отфильтрованных по id с пагинацией. Можно фильтровать и сортировать с "
                    "помощью параметров"
                    " запроса.",
        parameters=[
            OpenApiParameter(name='category', description='Фильтрация по ID категории', required=False,
                             type=OpenApiTypes.INT),
            OpenApiParameter(name='sort', description='Сортировка по полю (например, price, date, reviews)',
                             required=False, type=OpenApiTypes.STR),
            OpenApiParameter(name='sortType', description='Тип сортировки: inc (возрастание) или dec (убывание)',
                             required=False, type=OpenApiTypes.STR),
        ],
        responses={
            200: ProductSerializer,
            404: OpenApiResponse(description="Продукт по id не был найден"),
        }
    ),
    create=extend_schema(exclude=True),
    update=extend_schema(exclude=True),
    partial_update=extend_schema(exclude=True),
    destroy=extend_schema(exclude=True),
)
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
        "rating",
    ]

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(review_count=Count('reviews'), rating=Avg('reviews__rate'))
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


class CurrentUser(APIView):
    @extend_schema(exclude=True)
    def get(self, request):
        if request.user.is_authenticated:
            return Response({'username': request.user.username, 'email': request.user.email}, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_200_OK)


class ReviewsProductViewSet(APIView):
    @extend_schema(
        summary="Добавление пользовательского отзыва",
        description=(
                "Этот метод позволяет пользователю добавить отзыв о товаре. "
                "Пользователь должен быть аутентифицирован. "
                "В запросе необходимо передать текст отзыва и рейтинг."
        ),
        request=ReviewsSerializer,
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=ReviewsSerializer(many=True),
                description="Список отзывов для данного товара после добавления нового отзыва."
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=None,
                description="Некорректные данные в запросе."
            ),
        },
    )
    def post(self, request, id):
        Reviews.objects.get_or_create(product_id=int(id),
                                      author=request.user,
                                      text=request.data['text'],
                                      rate=int(request.data['rate']))
        reviews = Reviews.objects.filter(product_id=int(id))
        return Response(ReviewsSerializer(reviews, many=True, read_only=True).data, status=status.HTTP_200_OK)


class CategoriesView(APIView):
    @extend_schema(
        summary="Получить список категорий",
        description="Этот эндпоинт возвращает список категорий",
        responses={
            status.HTTP_200_OK: CategorySerializer(many=True),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Ошибка запроса, например, неверные параметры"),
        },
    )
    def get(self, request: Request):
        categories = Category.objects.filter(parent__isnull=True)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema_view(
    list=extend_schema(summary="Список популярных продуктов",
                       description="Получает список популярных продуктов"),
    create=extend_schema(exclude=True),
    update=extend_schema(exclude=True),
    partial_update=extend_schema(exclude=True),
    destroy=extend_schema(exclude=True),
    retrieve=extend_schema(exclude=True)
)
class PopularProductViewSet(ModelViewSet):
    queryset = Product.objects.prefetch_related("images").filter(available=True).order_by('-count')[:8]
    pagination_class = None
    serializer_class = ProductSerializer


@extend_schema_view(
    list=extend_schema(summary="Список продуктов ограниченного тиража",
                       description="Получает список продуктов ограниченного тиража"),
    create=extend_schema(exclude=True),
    update=extend_schema(exclude=True),
    partial_update=extend_schema(exclude=True),
    destroy=extend_schema(exclude=True),
    retrieve=extend_schema(exclude=True)
)
class LimitedProductViewSet(ModelViewSet):
    queryset = Product.objects.prefetch_related("images").filter(available=True, limited=True).all()
    pagination_class = None
    serializer_class = ProductSerializer


@extend_schema_view(
    list=extend_schema(summary="Список тэгов продукта",
                       description="Получает список тэгов продукта"),
    create=extend_schema(exclude=True),
    update=extend_schema(exclude=True),
    partial_update=extend_schema(exclude=True),
    destroy=extend_schema(exclude=True),
)
class TagsViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    pagination_class = None
    serializer_class = TagSerializer
