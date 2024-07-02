from django.db import models
from libs.base_model import BaseModelGeneric
from django.utils.translation import gettext_lazy as _
from person.models import Person


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
    person = models.ForeignKey(
        Person,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_person",
    )

    @property
    def last_checkin(self):
        from activity.models import CheckIn, LPR

        last_check_in_ts = 0
        activity_check_in_ts = (
            CheckIn.objects.filter(vehicle=self).order_by("-check_in_timestamp").frist()
        )
        if activity_check_in_ts:
            last_check_in_ts = activity_check_in_ts.check_in_timestamp

        lpr_check_in_ts = (
            LPR.objects.filter(
                vehicle=self,
                direction__iexact="in",
                time_utc_timestamp__gt=last_check_in_ts,
            )
            .order_by("-time_utc_timestamp")
            .first()
        )
        if lpr_check_in_ts:
            last_check_in_ts = lpr_check_in_ts.time_utc_timestamp

        return last_check_in_ts

    @property
    def last_checkin_str(self):
        from datetime import datetime

        ts = self.last_checkin
        if not ts:
            return
        dt = datetime.fromtimestamp(ts / 1000)
        formatted_string = dt.strftime("%d %b %Y %H:%M:%S")

        return formatted_string

    class Meta:
        verbose_name = _("Vehicle")
        verbose_name_plural = _("Vehicles")
