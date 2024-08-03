from django.urls import path, include
from .views import (user_sign_in,
                    user_sign_out,
                    user_sign_up,
                    user_profile,
                    user_avatar,
                    user_update_password)
from rest_framework.routers import DefaultRouter

app_name = "accountapp"

# accountrouter = DefaultRouter(trailing_slash=False)
# accountrouter.register(r"profile", ProfileViewSet)

urlpatterns = [
    path("sign-up", user_sign_up, name="sign-up"),
    path("sign-in", user_sign_in, name="sign-in"),
    path("sign-out", user_sign_out, name="sign-out"),
    path("profile", user_profile, name="profile"),
    path('profile/avatar', user_avatar, name="avatar"),
    path('profile/password', user_update_password, name="update_pasword")
    # path("", include(accountrouter.urls), name="profile"),
]
