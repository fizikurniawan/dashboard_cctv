from rest_framework.routers import DefaultRouter
from .views import SignInViewSet, RefreshTokenViewSet, MeViewSet

router = DefaultRouter()
router.register("sign-in", SignInViewSet, basename="sign-in")
router.register("refresh", RefreshTokenViewSet, basename="refresh")
router.register("me", MeViewSet, basename="me")
