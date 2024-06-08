from django.db import models
from libs.base_model import BaseModelGeneric

class VehicleType(BaseModelGeneric):
    name = models.CharField()

class Vehicle(BaseModelGeneric):
    license_plate_number = models.CharField(max_length=20)
    vehicle_type = models.CharField(max_length=20)
    owner_full_name = models.CharField(max_length=255)

    