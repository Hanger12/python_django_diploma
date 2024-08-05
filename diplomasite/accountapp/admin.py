from django.contrib import admin
from .models import Profile


# Register your models here.

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = "user_verbose", "middle_name", "phone", "avatar"

    def get_queryset(self, request):
        return Profile.objects.select_related("user")

    def user_verbose(self, obj: Profile) -> str:
        return obj.user.first_name or obj.user.username
