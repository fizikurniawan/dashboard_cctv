from rest_framework.routers import DefaultRouter
from .views import FileViewSet, ConfigurationViewSet

router = DefaultRouter()
router.register("file", FileViewSet, basename="file")
router.register("config", ConfigurationViewSet, basename="config")
