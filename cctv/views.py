from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from libs.pagination import CustomPagination
from .models import Camera, LPR
from .serializers import CameraSerializer, LPRSerializer
from django_filters import rest_framework as django_filters


class CameraFilterset(django_filters.FilterSet):
    is_gate = django_filters.BooleanFilter(field_name="is_gate", lookup_expr="exact")
    is_active = django_filters.BooleanFilter(
        field_name="is_active", lookup_expr="exact"
    )


class LPRFilterset(django_filters.FilterSet):
    channel_id = django_filters.CharFilter(field_name="channel_id", lookup_expr="exact")


class CameraViewSet(viewsets.ModelViewSet):
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter, django_filters.DjangoFilterBackend)
    search_fields = ("name", "channel_id")
    permission_classes = (IsAuthenticated, DjangoModelPermissions)
    queryset = Camera.objects.filter()
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    serializer_class = CameraSerializer
    filterset_class = CameraFilterset
    lookup_field = "id32"


class LPRViewSet(viewsets.ModelViewSet):
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = (
        "plate_number",
        "vehicle__owner__full_name",
        "vehicle__owner__no_id",
    )
    permission_classes = (IsAuthenticated, DjangoModelPermissions)
    queryset = LPR.objects.filter()
    http_method_names = ["get", "head", "options"]
    serializer_class = LPRSerializer
    lookup_field = "uuid"
    filterset_class = LPRFilterset
