from rest_framework import viewsets, filters, decorators, response
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from libs.pagination import CustomPagination
from .models import Camera, LPR, Location, CommandCenter
from .serializers import (
    CameraSerializer,
    LPRSerializer,
    LocationSerializer,
    CommandCenterReadSerializer,
    CommandCenterWriteSerializer,
)
from django_filters import rest_framework as django_filters
from django.shortcuts import get_object_or_404
from datetime import datetime, time
from django.utils.timezone import make_aware


class CameraFilterset(django_filters.FilterSet):
    is_gate = django_filters.BooleanFilter(field_name="is_gate", lookup_expr="exact")
    is_active = django_filters.BooleanFilter(
        field_name="is_active", lookup_expr="exact"
    )
    location_id32 = django_filters.CharFilter(
        field_name="location__id32", lookup_expr="exact"
    )


class LPRFilterset(django_filters.FilterSet):
    channel_id = django_filters.CharFilter(field_name="channel_id", lookup_expr="exact")


class LocationViewSet(viewsets.ModelViewSet):
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name", "description")
    permission_classes = (IsAuthenticated, DjangoModelPermissions)
    queryset = Location.objects.filter()
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    serializer_class = LocationSerializer
    lookup_field = "id32"


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

    @decorators.action(
        methods=["GET"], detail=False, url_path=r"(?P<channel_id>[^/.]+)/statistic"
    )
    def get_statistic(self, request, channel_id=None):
        get_object_or_404(Camera, channel_id=channel_id)
        today = datetime.now().date()

        # Combine the current date with the time 00:00:00 and 23:59:59
        start_of_today = (
            make_aware(datetime.combine(today, time.min)).timestamp() * 1000
        )
        end_of_today = make_aware(datetime.combine(today, time.max)).timestamp() * 1000
        lpr = LPR.objects.filter(
            vehicle__isnull=False,
            channel_id=channel_id,
            time_utc_timestamp__gte=start_of_today,
            time_utc_timestamp__lte=end_of_today,
        )

        total_movement = lpr.count()
        total_visitor = len(list(set(lpr.values_list("vehicle_id", flat=True))))

        return response.Response(
            {"total_movement": total_movement, "total_visitor": total_visitor}
        )


class LPRViewSet(viewsets.ModelViewSet):
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter, django_filters.DjangoFilterBackend)
    search_fields = (
        "number_plate",
        "vehicle__owner__full_name",
        "vehicle__owner__no_id",
    )
    permission_classes = (IsAuthenticated, DjangoModelPermissions)
    queryset = LPR.objects.filter()
    http_method_names = ["get", "head", "options"]
    serializer_class = LPRSerializer
    lookup_field = "uuid"
    filterset_class = LPRFilterset


class CommandCenterViewSet(viewsets.ModelViewSet):
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ("cameras__channel_id", "cameras__location__name", "name")
    permission_classes = (IsAuthenticated, DjangoModelPermissions)
    queryset = CommandCenter.objects.filter()
    http_method_names = ["get", "head", "options", "post", "put", "delete"]
    lookup_field = "id32"

    def get_serializer_class(self):
        if self.action in ["create", "update"]:
            return CommandCenterWriteSerializer
        return CommandCenterReadSerializer
