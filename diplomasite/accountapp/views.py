from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, parsers
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, action, parser_classes, permission_classes
from rest_framework.parsers import JSONParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_200_OK
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ViewSet
from ast import literal_eval
from io import BytesIO
from .models import Profile
from .serializers import UserSerializer, ProfileSerializer


# class UserViewSet(ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializers
#
#     @action(detail=False, methods=["post"], parser_classes=[parsers.JSONParser, ])
#     @csrf_exempt
#     def sign_up(self, request):
#         print("zdec:" + request)
#         return Response({
#             "blat pochemu ne robit": 3
#         }, status=status.HTTP_201_CREATED)

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


@api_view(["POST"])
def user_sign_up(request: Request) -> Response:
    """Функция 'user_sign_up': обрабатывает POST запрос на регистрацию пользователя"""
    if request.method == 'POST':
        stream = BytesIO(request.body)
        data = JSONParser().parse(stream)
        serializer = UserSerializer(data={"first_name": data['name'],
                                          "username": data['username'],
                                          "password": data['password']})
        if serializer.is_valid():
            serializer.save()
            user = authenticate(request, username=data['username'],
                                password=data['password'])
            login(request=request, user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


# class ProfileViewSet(ModelViewSet):
#     queryset = Profile.objects.select_related('user').all()
#     serializer_class = ProfileSerializer

@api_view(["POST", "GET"])
def user_profile(request: Request) -> Response:
    if request.method == "GET":
        return Response({
            "fullName": "hord6",
            "email": "asdasda@mail.ru",
            "phone": "88002000600",
        }, status=HTTP_200_OK)
