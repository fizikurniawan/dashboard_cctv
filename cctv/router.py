from rest_framework.routers import DefaultRouter
from .views import CameraViewSet, LPRViewSet, LocationViewSet, CommandCenterViewSet

router = DefaultRouter()
router.register("location", LocationViewSet, basename="location")
router.register("camera", CameraViewSet, basename="camera")
router.register("lpr", LPRViewSet, basename="lpr")
router.register("command-center", CommandCenterViewSet, basename="command-center")
