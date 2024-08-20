from rest_framework.routers import DefaultRouter
from .views import StatisticViewSet

router = DefaultRouter()
router.register("", StatisticViewSet, basename="statistic")
