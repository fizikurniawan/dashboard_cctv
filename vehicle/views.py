import datetime
from django_filters import rest_framework as django_filters
from django.shortcuts import HttpResponse
from rest_framework import viewsets, filters, decorators
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from libs.filter import CreatedAtFilterMixin
from libs.pagination import CustomPagination
from .models import Vehicle, VehicleType
from activity.models import LPR
from .serializers import (
    VehicleSerializer,
    VehicleWriteSerializer,
    VehicleTypeSerializer,
)
from libs import constants
from libs.csv import create_csv_file
from libs.permission import RBACPermission


class VehicleFilter(CreatedAtFilterMixin):
    person_id32 = django_filters.CharFilter(
        field_name="person__id32", lookup_expr="exact"
    )


class VehicleTypeViewSet(viewsets.ModelViewSet):
    queryset = VehicleType.objects.all().order_by("-created_at")
    serializer_class = VehicleTypeSerializer
    lookup_field = "id32"
    permission_classes = [IsAuthenticated, RBACPermission]
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    PERMISSION_REQUIRES = {
        constants.PRINCIPAL_ROLE: [
            "list",
            "create",
            "retrieve",
            "partial_update",
            "destroy",
        ],
        constants.SUPERADMIN_ROLE: [
            "list",
            "retrieve",
        ],
    }


class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.filter().order_by("-created_at")
    lookup_field = "id32"
    permission_classes = [IsAuthenticated, RBACPermission]
    pagination_class = CustomPagination
    filterset_class = VehicleFilter
    filter_backends = (filters.SearchFilter, django_filters.DjangoFilterBackend)
    search_fields = ("owner__full_name", "owner__no_id", "license_plate_number")
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    PERMISSION_REQUIRES = {
        constants.PRINCIPAL_ROLE: [
            "list",
            "create",
            "retrieve",
            "partial_update",
            "destroy",
            "get_csv",
        ],
        constants.SUPERADMIN_ROLE: [
            "list",
            "create",
            "retrieve",
            "partial_update",
            "destroy",
            "get_csv",
        ],
    }

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

    @decorators.action(methods=["GET"], detail=False, url_path="csv")
    def get_csv(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        data = []
        for q in queryset:
            data.append(
                {
                    "ID": q.id32,
                    "Nomor Kendaraan": q.license_plate_number,
                    "Tipe Kendaraan": q.vehicle_type.name,
                    "Pemilik": q.owner.full_name,
                    "Last Checkin": q.last_checkin_str,
                }
            )

        output = create_csv_file(data)
        filename = f"vehicle_{datetime.datetime.now().strftime('%Y-%m-%d')}.csv"
        http_response = HttpResponse(
            output,
            content_type="text/csv",
        )
        http_response["Content-Disposition"] = "attachment; filename=%s" % filename
        http_response["Access-Control-Expose-Headers"] = "Content-Disposition"

        return http_response
