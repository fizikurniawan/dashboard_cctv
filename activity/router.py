from rest_framework.routers import DefaultRouter
from .views import LPRViewSet, CheckInViewSet, CheckOutViewSet

router = DefaultRouter()
router.register("lpr", LPRViewSet, basename="lpr")
router.register("check-in", CheckInViewSet, basename="check-in")
router.register("check-out", CheckOutViewSet, basename="check-out")
