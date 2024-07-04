from rest_framework.routers import DefaultRouter
from .views import FileViewSet, ConfigurationViewSet, PurposeOfVisitViewSet

router = DefaultRouter()
router.register("file", FileViewSet, basename="file")
router.register("config", ConfigurationViewSet, basename="config")
router.register("purpose-of-visit", PurposeOfVisitViewSet, basename="purpose-of-visit")
