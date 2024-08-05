from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from io import BytesIO
from .models import Profile
from .serializers import UserCreateSerializer, ProfileSerializer, ChangePasswordSerializer, ProfileUpdateSerializer
from nameparser import HumanName

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
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST", "GET"])
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


@api_view(["POST"])
@parser_classes([MultiPartParser, ])
def user_avatar(request: Request) -> Response:
    if request.method == "POST":
        profile = Profile.objects.get(user=request.user)
        profile.avatar = request.FILES['avatar']
        profile.save()
        return Response(status=status.HTTP_201_CREATED)


@api_view(["POST"])
def user_update_password(request: Request) -> Response:
    if request.method == "POST":
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "Пароль успешно изменен"}, status=status.HTTP_200_OK)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
