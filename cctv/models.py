from uuid import uuid4
from django.db import models
from django.conf import settings
from libs.base_model import BaseModelGeneric
from django.utils.translation import gettext_lazy as _
from vehicle.models import Vehicle, Resident


class Location(BaseModelGeneric):
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.id32} {self.name}"

    class Meta:
        verbose_name = _("Location")
        verbose_name_plural = _("Locations")


class Camera(BaseModelGeneric):
    channel_id = models.CharField(max_length=150)
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField()
    is_gate = models.BooleanField(default=False)
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f"{self.channel_id} {self.name}"

    @property
    def hls_url(self):
        HLS_BASE_URL = getattr(settings, "HLS_BASE_URL", "http://172.105.124.43:8006")

        return f"{HLS_BASE_URL}/{self.channel_id}.m3u8"

    class Meta:
        verbose_name = _("Camera")
        verbose_name_plural = _("Cameras")


class LPR(models.Model):
    DIRECTION_CHOICES = (("in", "IN"), ("out", "OUT"), ("unknown", "UNKNOWN"))
    uuid = models.UUIDField(default=uuid4, editable=False)
    channel_id = models.CharField(max_length=100)
    camera = models.ForeignKey(Camera, on_delete=models.SET_NULL, null=True, blank=True)
    number_plate = models.CharField(max_length=100)
    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.SET_NULL, null=True, blank=True
    )
    direction = models.CharField(choices=DIRECTION_CHOICES, max_length=20)
    time_utc_timestamp = models.BigIntegerField()

    def __str__(self):
        return f"{self.channel_id} - {self.number_plate} - {self.direction} - {self.time_utc_str}"

    @property
    def doc_type_dict(self):
        return {
            "value": self.doc_type,
            "text": dict(self.DOC_TYPE_CHOICES).get(self.doc_type, ""),
        }

    @property
    def full_name(self):
        if not self.vehicle:
            return
        return self.vehicle.owner.full_name

    @property
    def no_id(self):
        if not self.vehicle:
            return
        return self.vehicle.owner.no_id

    @property
    def time_utc_str(self):
        from libs.moment import convert_timestamp_ms_to_date

        return convert_timestamp_ms_to_date(self.time_utc_timestamp)


class CommandCenter(BaseModelGeneric):
    name = models.CharField(max_length=250)
    cameras = models.ManyToManyField(Camera)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("Command Center")
        verbose_name_plural = _("Command Centers")
