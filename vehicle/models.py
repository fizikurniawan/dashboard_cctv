from django.db import models
from libs.base_model import BaseModelGeneric
from django.utils.translation import gettext_lazy as _


class VehicleType(BaseModelGeneric):
    name = models.CharField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Vehicle Type")
        verbose_name_plural = _("Vehicle Types")


class Vehicle(BaseModelGeneric):
    license_plate_number = models.CharField(max_length=250)
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.SET_NULL, null=True, blank=True)
    owner_full_name = models.CharField(max_length=255)
    owner_contact = models.CharField(max_length=100)
    code = models.CharField(max_length=100)

    class Meta:
        verbose_name = _("Vehicle")
        verbose_name_plural = _("Vehicles")
