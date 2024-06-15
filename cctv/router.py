from rest_framework.routers import DefaultRouter
from .views import CameraViewSet, LPRViewSet

router = DefaultRouter()
router.register("camera", CameraViewSet, basename="camera")
router.register("lpr", LPRViewSet, basename="lpr")
