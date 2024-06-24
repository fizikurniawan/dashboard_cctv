from django.db import models
from libs.base_model import BaseModelGeneric
from django.utils.translation import gettext_lazy as _
from resident.models import Resident


class VehicleType(BaseModelGeneric):
    name = models.CharField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Vehicle Type")
        verbose_name_plural = _("Vehicle Types")


class Vehicle(BaseModelGeneric):
    license_plate_number = models.CharField(max_length=250)
    vehicle_type = models.ForeignKey(
        VehicleType, on_delete=models.SET_NULL, null=True, blank=True
    )
    owner = models.ForeignKey(
        Resident, on_delete=models.SET_NULL, null=True, blank=True
    )

    @property
    def last_checkin(self):
        from cctv.models import LPR

        instance = (
            LPR.objects.filter(vehicle=self, direction__iexact="in")
            .order_by("-time_utc_timestamp")
            .first()
        )
        if not instance:
            return
        return instance.time_utc_timestamp

    @property
    def last_checkin_str(self):
        from datetime import datetime

        ts = self.last_checkin
        if not ts:
            return
        dt = datetime.fromtimestamp(ts/1000)
        formatted_string = dt.strftime("%d %b %Y %H:%M:%S")

        return formatted_string

    class Meta:
        verbose_name = _("Vehicle")
        verbose_name_plural = _("Vehicles")
