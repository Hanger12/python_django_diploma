from django.contrib.auth.models import User
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


def profile_avatar_directory_path(instance: "Profile", filename: str) -> str:
    return "profile/user_{pk}/avatar/{filename}".format(pk=instance.user, filename=filename)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    middle_name = models.CharField(max_length=100, null=False, blank=True)
    phone = models.CharField(unique=True, max_length=11, null=True, blank=True)
    avatar = models.ImageField(null=True, blank=True, upload_to=profile_avatar_directory_path)

    @property
    def fullName(self):
        return f"{self.user.last_name} {self.user.first_name} {self.middle_name}"

    @property
    def avatar_info(self):
        if self.avatar:
            return {"src": self.avatar.url, "alt": self.avatar.name}
        return None
