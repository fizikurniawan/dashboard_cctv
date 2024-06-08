from django.db import models
from django.contrib.auth.models import User


class AuthToken(models.Model):
    token = models.CharField(max_length=500)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    issued_at = models.DateTimeField(auto_now_add=True)
    device_id = models.CharField(max_length=150, null=True, blank=True)

    class Meta:
        verbose_name = "Auth Token"
        verbose_name_plural = "Auth Tokens"
