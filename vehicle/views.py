from django_filters import rest_framework as django_filters
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from libs.filter import CreatedAtFilterMixin
from libs.pagination import CustomPagination
from .models import Vehicle, VehicleType
from cctv.models import LPR
from .serializers import (
    VehicleSerializer,
    VehicleWriteSerializer,
    VehicleTypeSerializer,
)


class VehicleFilter(CreatedAtFilterMixin):
    owner_id32 = django_filters.CharFilter(
        field_name="owner__id32", lookup_expr="exact"
    )


class VehicleTypeViewSet(viewsets.ModelViewSet):
    queryset = VehicleType.objects.all().order_by("-created_at")
    serializer_class = VehicleTypeSerializer
    lookup_field = "id32"
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]


class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.filter().order_by("-created_at")
    lookup_field = "id32"
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    pagination_class = CustomPagination
    filterset_class = VehicleFilter
    filter_backends = (filters.SearchFilter, django_filters.DjangoFilterBackend)
    search_fields = ("owner__full_name", "owner__no_id", "license_plate_number")
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def perform_create(self, serializer):
        instance = serializer.save()

        # update LPR with plate
        LPR.objects.filter(number_plate=instance.license_plate_number).update(
            vehicle=instance
        )

    def get_serializer_class(self, *args, **kwargs):
        if self.action in ["create"]:
            return VehicleWriteSerializer
        return VehicleSerializer
