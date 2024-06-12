from django.db import models
from django.conf import settings
from libs.base_model import BaseModelGeneric
from django.utils.translation import gettext_lazy as _


class Camera(BaseModelGeneric):
    channel_id = models.CharField(max_length=150)
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.channelId} {self.name}"

    @property
    def hls_url(self):
        HLS_BASE_URL = getattr(settings, "HLS_BASE_URL", "http://172.105.124.43:8006")

        return f"{HLS_BASE_URL}/{self.channel_id}.m3u8"

    class Meta:
        verbose_name = _("Camera")
        verbose_name_plural = _("Cameras")
