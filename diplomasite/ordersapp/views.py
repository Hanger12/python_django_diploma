import random

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiSchemaBase, OpenApiParameter, OpenApiRequest
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from basketapp.models import Cart
from ordersapp.docserializers import OrderDocSerializer
from ordersapp.models import Order, DeliverySettings, OrderItem
from ordersapp.serializers import OrderSerializer, DeliverySettingsSerializer
from shopapp.models import Product


class OrdersView(APIView):
    @extend_schema(summary="Получение истории заказов пользователя",
                   description="Получает список заказов пользователя по id пользователя, "
                               "он должен быть авторизован",

                   responses={
                       200: OpenApiResponse(
                           description="Список заказов пользователя успешно получен.",
                           response=OrderSerializer(many=True),
                       ),
                   }
                   )
    def get(self, request):
        queryset = Order.objects.filter(user=request.user)
        serializer_class = OrderSerializer(queryset, many=True)
        return Response(serializer_class.data, status=status.HTTP_200_OK)

    @extend_schema(summary="Создание заказа из корзины товаров",
                   description="Обрабатывает пост запрос на создание заказа из корзины товаров, "
                               "пользователь должен быть авторизован",
                   request={
                       "application/json": {
                           "example": [
                               {"id": 1, "count": 2},
                               {"id": 5, "count": 1}
                           ]
                       }
                   },
                   responses={
                       201: {
                           "type": "object",
                           "properties": {
                               "orderId": {
                                   "type": "integer",
                                   "description": "Идентификатор заказа."
                               }
                           },
                           "required": ["orderId"]
                       }
                   })
    def post(self, request):
        if request.user.is_authenticated:
            products_ids = []
            order = Order.objects.create(user=request.user)
            for data in request.data:
                product_id = data.pop('id')
                count = data.get('count')
                product = Product.objects.get(id=product_id)
                OrderItem.objects.create(order=order, product=product, count=count)
            return Response({"orderId": order.pk}, status=status.HTTP_201_CREATED)


@extend_schema(exclude=True)
class DeliverySettingsViewSet(ModelViewSet):
    queryset = DeliverySettings.objects.all()
    serializer_class = DeliverySettingsSerializer


class OrderView(APIView):
    @extend_schema(
        summary="Получение данных заказа",
        description="Возвращает данные заказа по указанному идентификатору.",
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                description="Успешный ответ с данными заказа",
                response=OrderDocSerializer
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                description="Заказ не найден"
            ),
        }
    )
    def get(self, request, id):
        order = Order.objects.get(id=id)
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Обновление существующего заказа",
        description="Частично обновляет существующий заказ по указанному идентификатору. Требуется ID заказа и данные "
                    "для обновления.",
        request=OrderSerializer,
        responses={
            200: OpenApiResponse(
                description="Успешный ответ с обновленными данными заказа",
                response=OrderDocSerializer
            ),
            400: OpenApiResponse(
                description="Неверные входные данные"
            ),
            404: OpenApiResponse(
                description="Заказ не найден"
            ),
        }
    )
    def post(self, request, id):
        order = Order.objects.get(id=id)
        order_ser = OrderSerializer(instance=order, data=request.data, partial=True)
        if order_ser.is_valid():
            order_ser.save()
        print(order_ser.data)
        return Response(request.data, status=status.HTTP_200_OK)


class PayMentView(APIView):
    @extend_schema(
        summary="Обработка оплаты заказа",
        request={
            "application/json": {
                "example": {
                    "number": "9999999999999999",
                    "name": "Annoying Orange",
                    "month": "02",
                    "year": "2025",
                    "code": "123"
                }
            }
        },
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                description='Заказ успешно обработан.',
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description='Некорректный запрос или ошибка валидации.',
            ),
        },
        description=(
                'Обрабатывает заказ в зависимости от переданного числа. Если число четное и не оканчивается на 0, '
                'то обновляются связанные с заказом позиции, а статус заказа устанавливается как "принят". Если число '
                'нечетное или оканчивается на 0, статус заказа устанавливается как "Ошибка" со случайным сообщением об '
                'ошибке.'
                'Поле "number" обязательно, остальные поля учитываются, но не влияют на логику обработки заказа.'
        ),
    )
    def post(self, request, id):
        order = Order.objects.get(id=id).only('id')
        number = request.data['number']
        if int(number) % 2 == 0 and not number.endswith('0'):
            order_items = OrderItem.objects.filter(order=order).prefetch_related('products')
            for item in order_items:
                item.product.count += item.count
                item.product.save()
            order.status = "accepted"
            order.paymentError = 'undefined'
        else:
            order.status = 'Failed'
            order.paymentError = f"Ошибка: {random.choice(["Ошибка сети", "Проблемы с картой", "Неизвестная ошибка"])}"
        order.save()
        cart = Cart.objects.get(user=request.user)
        cart.delete()
        return Response(status=status.HTTP_200_OK)
