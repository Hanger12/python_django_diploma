from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from io import BytesIO
from .models import Profile
from .serializers import UserCreateSerializer, ProfileSerializer, ChangePasswordSerializer, ProfileUpdateSerializer


@extend_schema(
    summary="Вход пользователя",
    description="Эндпоинт для авторизации пользователя по логину и паролю.",
    request={
        'application/json': {
            "type": "object",
            "properties": {
                "username": {"type": "string", "description": "login пользователя"},
                "password": {"type": "string", "description": "Пароль"},
            },
            "required": ["username", "password"],
        }
    },
    responses={
        200: OpenApiResponse(description="Пользователь успешно аутентифицирован"),
        401: OpenApiResponse(description="Неверные учетные данные")
    },
)
@api_view(['POST'])
@csrf_exempt
def user_sign_in(request: Request, format=None) -> Response:
    """Метод, обрабатывающий POST запрос на вход пользователя"""
    if request.method == 'POST':
        stream = BytesIO(request.body)
        data = JSONParser().parse(stream)
        username = data.get("username")
        password = data.get("password")
        user = None
        if not user:
            user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return Response({"User": user.is_authenticated}, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


@extend_schema(
    summary="Выход пользователя",
    description="Эндпоинт для выхода пользователя",
    responses={
        200: OpenApiResponse(description="Выход успешен"),
        400: OpenApiResponse(description="пользователь не был аутентифицирован")
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def user_sign_out(request: Request) -> Response:
    """Функция 'user_signout': обрабатывает POST запрос на выход пользователя"""
    if request.method == 'POST':
        try:
            logout(request)
            return Response(status=status.HTTP_200_OK)
        except Exception as exp:
            return Response({"Error": str(exp)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Регистрация пользователя",
    request={
        'application/json': {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Имя пользователя"},
                "username": {"type": "string", "description": "login пользователя"},
                "password": {"type": "string", "description": "Пароль"},

            },
            "required": ["name", "username", "password"],
        }
    },
    responses={
        200: OpenApiResponse(description="Пользователь успешно зарегистрирован"),
        400: OpenApiResponse(description="Такой пользователь уже существует")
    }
)
@api_view(["POST"])
def user_sign_up(request: Request) -> Response:
    """Функция 'user_sign_up': обрабатывает POST запрос на регистрацию пользователя"""
    if request.method == 'POST':
        stream = BytesIO(request.body)
        data = JSONParser().parse(stream)
        serializer = UserCreateSerializer(data={"first_name": data['name'],
                                                "username": data['username'],
                                                "password": data['password']})
        if serializer.is_valid():
            serializer.save()
            print(serializer.data)
            user = authenticate(request, username=data['username'],
                                password=data['password'])
            login(request=request, user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Получение и обновление профиля пользователя",
    description="Получение информации о профиле пользователя (GET) и обновление информации о профиле (POST).",
    request=ProfileUpdateSerializer,
    responses={
        200: ProfileSerializer,
        400: OpenApiResponse(description="Ошибка валидации данных"),
        401: OpenApiResponse(description="Необходима аутентификация")
    }
)
@api_view(["POST", "GET"])
@permission_classes([IsAuthenticated])
def user_profile(request: Request) -> Response:
    profile = request.user.profile
    if request.method == "GET":
        serializer = ProfileSerializer(profile)
        # print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    if request.method == "POST":
        print(request.data)
        fullName = request.data.get("fullName").split()
        first_name = ""
        middle_name = ""
        last_name = ""
        if len(fullName) == 2:
            first_name = fullName[1]
            last_name = fullName[0]
        elif len(fullName) == 3:
            first_name = fullName[1]
            middle_name = fullName[2]
            last_name = fullName[0]
        elif len(fullName) == 1:
            first_name = fullName[0]
        avatar = request.data.get('avatar')
        data = {
            'avatar': avatar["alt"] if avatar else None,
            'middle_name': middle_name,
            'phone': request.data.get("phone"),
            'user': {'first_name': first_name, 'email': request.data.get("email"), 'last_name': last_name}
        }
        serializer = ProfileUpdateSerializer(instance=profile, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(ProfileSerializer(profile).data, status=status.HTTP_200_OK)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Обновление аватара пользователя",
    description=(
            "Этот метод позволяет пользователю загрузить и обновить свой аватар. "
            "Запрос должен содержать файл аватара в формате multipart/form-data. "
            "После успешного обновления аватара возвращается статус 201 Created."
    ),
    request={"type": "object",
             "properties": {
                 "avatar": {
                     "type": "string",
                     "format": "binary",
                     "description": "Файл изображения для аватара пользователя"
                 }
             },
             "required": ["avatar"]
             },
    responses={
        status.HTTP_201_CREATED: OpenApiResponse(
            response=None,
            description="Аватар успешно обновлён."
        ),
        status.HTTP_400_BAD_REQUEST: OpenApiResponse(
            response=None,
            description="Ошибка в запросе. Возможно, файл аватара не был предоставлен."
        ),
    },
)
@api_view(["POST"])
@parser_classes([MultiPartParser, ])
def user_avatar(request: Request) -> Response:
    if request.method == "POST":
        profile = Profile.objects.get(user=request.user)
        profile.avatar = request.FILES['avatar']
        profile.save()
        return Response(status=status.HTTP_201_CREATED)


@extend_schema(
    summary="Обновление пароля пользователя",
    description="Этот эндпоинт позволяет пользователю изменить свой пароль. Необходимо предоставить старый и новый "
                "пароль в теле запроса.",
    request=ChangePasswordSerializer,
    responses={
        200: OpenApiResponse(
            description="Пароль успешно изменен",
        ),
        400: OpenApiResponse(
            description="Ошибки валидации данных",
        )
    }
)
@api_view(["POST"])
def user_update_password(request: Request) -> Response:
    if request.method == "POST":
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "Пароль успешно изменен"}, status=status.HTTP_200_OK)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
