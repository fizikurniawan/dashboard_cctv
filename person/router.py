from rest_framework.routers import DefaultRouter
from .views import PersonViewSet

router = DefaultRouter()
router.register("person", PersonViewSet, basename="person")
