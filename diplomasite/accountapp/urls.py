from django.urls import path, include
from .views import user_sign_in, user_sign_out, user_sign_up, user_profile
from rest_framework.routers import DefaultRouter

app_name = "accountapp"

# accountrouter = DefaultRouter()
# accountrouter.register("sign-up", UserViewSet)

urlpatterns = [
    path("sign-up", user_sign_up, name="sign-up"),
    path("sign-in", user_sign_in, name="sign-in"),
    path("sign-out", user_sign_out, name="sign-out"),
    path("profile", user_profile, name='profile'),
]
