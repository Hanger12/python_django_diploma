from django.contrib.auth.models import User
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


def profile_avatar_directory_path(instance: "Profile", filename: str) -> str:
    return "Profiles/user_{pk}/avatar/{filename}".format(pk=instance.user, filename=filename)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    middle_name = models.CharField(max_length=100, null=False, blank=True)
    phone_number = PhoneNumberField(unique=True, null=True, blank=True)
    avatar = models.ImageField(null=True, blank=True, upload_to=profile_avatar_directory_path)
