from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RoleViewSet

router = DefaultRouter()
router.register("user", UserViewSet, basename="user")
router.register("role", RoleViewSet, basename="role")
