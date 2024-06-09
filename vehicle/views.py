from django_filters import rest_framework as django_filters
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from libs.filter import CreatedAtFilterMixin
from libs.pagination import CustomPagination
from .models import Vehicle, VehicleType
from .serializers import (
    VehicleSerializer,
    VehicleWriteSerializer,
    VehicleTypeSerializer,
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
    filterset_class = CreatedAtFilterMixin
    filter_backends = (filters.SearchFilter, django_filters.DjangoFilterBackend)
    search_fields = ("owner_full_name", "owner_contact", "license_plate_number")
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_serializer_class(self, *args, **kwargs):
        if self.action in ["create"]:
            return VehicleWriteSerializer
        return VehicleSerializer
