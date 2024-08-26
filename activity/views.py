from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from libs.pagination import CustomPagination
from libs.permission import RBACPermission
from libs import constants
from .models import LPR, CheckIn
from .serializers import LPRSerializer, CheckInSerializer, CheckOutSerializer
from django_filters import rest_framework as django_filters


class LPRFilterset(django_filters.FilterSet):
    channel_id = django_filters.CharFilter(field_name="channel_id", lookup_expr="exact")


class LPRViewSet(viewsets.ModelViewSet):
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter, django_filters.DjangoFilterBackend)
    search_fields = ("number_plate",)
    permission_classes = (IsAuthenticated,)
    queryset = LPR.objects.filter().order_by("-time_utc_timestamp")
    http_method_names = ["get", "head", "options"]
    serializer_class = LPRSerializer
    lookup_field = "uuid"
    filterset_class = LPRFilterset


class CheckInViewSet(viewsets.ModelViewSet):
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter, django_filters.DjangoFilterBackend)
    search_fields = (
        "person__full_name",
        "person__no_id",
        "vehicle__license_plate_number",
        "vehicle__vehicle_type__name",
    )
    permission_classes = (IsAuthenticated, RBACPermission)
    queryset = CheckIn.objects.filter().order_by("-created_at")
    http_method_names = ["get", "head", "options"]
    serializer_class = CheckInSerializer
    lookup_field = "uuid"

    PERMISSION_REQUIRES = {
        constants.PRINCIPAL_ROLE: [
            "list",
            "retrieve",
        ],
        constants.SUPERADMIN_ROLE: [
            "list",
            "retrieve",
        ],
    }


class CheckOutViewSet(viewsets.GenericViewSet, viewsets.mixins.CreateModelMixin):
    serializer_class = CheckOutSerializer
    permission_classes = (IsAuthenticated, RBACPermission)
    PERMISSION_REQUIRES = {
        constants.PRINCIPAL_ROLE: [
            "create",
        ],
        constants.SUPERADMIN_ROLE: [
            "create",
        ],
    }
