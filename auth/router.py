from rest_framework.routers import DefaultRouter
from .views import SignInViewSet, RefreshTokenViewSet

router = DefaultRouter()
router.register("sign-in", SignInViewSet, basename="sign-in")
router.register("refresh", RefreshTokenViewSet, basename="refresh")
