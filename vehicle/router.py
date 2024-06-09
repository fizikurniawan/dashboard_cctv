from rest_framework.routers import DefaultRouter
from .views import VehicleTypeViewSet, VehicleViewSet

router = DefaultRouter()
router.register("vehicle", VehicleViewSet, basename="vehicle")
router.register("vehicle-type", VehicleTypeViewSet, basename="vehicle-type")
