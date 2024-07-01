from rest_framework.routers import DefaultRouter
from .views import ResidentViewSet, VisitorViewSet

router = DefaultRouter()
router.register("resident", ResidentViewSet, basename="resident")
router.register("visitor", VisitorViewSet, basename="visitor")
