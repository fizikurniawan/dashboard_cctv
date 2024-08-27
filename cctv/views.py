from rest_framework import viewsets, filters, decorators, response
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from libs.pagination import CustomPagination
from .models import Camera, Location, CommandCenter
from activity.models import LPR
from .serializers import (
    CameraSerializer,
    LocationSerializer,
    CommandCenterReadSerializer,
    CommandCenterWriteSerializer,
)
from django_filters import rest_framework as django_filters
from django.shortcuts import get_object_or_404
from datetime import datetime, time
from django.utils.timezone import make_aware
from libs.eocortex import EocortexManager


class CameraFilterset(django_filters.FilterSet):
    is_gate = django_filters.BooleanFilter(field_name="is_gate", lookup_expr="exact")
    is_active = django_filters.BooleanFilter(
        field_name="is_active", lookup_expr="exact"
    )
    location_id32 = django_filters.CharFilter(
        field_name="location__id32", lookup_expr="exact"
    )


class LocationViewSet(viewsets.ModelViewSet):
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name", "description")
    permission_classes = (IsAuthenticated, )
    queryset = Location.objects.filter().order_by("-created_at")
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    serializer_class = LocationSerializer
    lookup_field = "id32"


class CameraViewSet(viewsets.ModelViewSet):
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter, django_filters.DjangoFilterBackend)
    search_fields = ("name", "channel_id")
    permission_classes = (IsAuthenticated, )
    queryset = Camera.objects.filter().order_by("-created_at")
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    serializer_class = CameraSerializer
    filterset_class = CameraFilterset
    lookup_field = "id32"

    # PTZ Control Actions
    @decorators.action(methods=["POST"], detail=True, url_path="ptz/zoom-in")
    def zoom_in(self, request, pk=None):
        camera = self.get_object()
        manager = EocortexManager()
        response_data = manager.step_zoom(camera.channel_id, zoom_step=5)  # Example step value
        return response.Response(response_data)

    @decorators.action(methods=["POST"], detail=True, url_path="ptz/zoom-out")
    def zoom_out(self, request, pk=None):
        camera = self.get_object()
        manager = EocortexManager()
        response_data = manager.step_zoom(camera.channel_id, zoom_step=-5)  # Example step value
        return response.Response(response_data)

    @decorators.action(methods=["POST"], detail=True, url_path="ptz/move")
    def move_camera(self, request, pk=None):
        camera = self.get_object()
        pan_speed = request.data.get("pan_speed", 0)
        tilt_speed = request.data.get("tilt_speed", 0)
        manager = EocortexManager()
        response_data = manager.continuous_move(camera.channel_id, pan_speed, tilt_speed)
        return response.Response(response_data)

    @decorators.action(methods=["POST"], detail=True, url_path="ptz/stop")
    def stop_movement(self, request, pk=None):
        camera = self.get_object()
        manager = EocortexManager()
        response_data = manager.stop_movement(camera.channel_id)
        return response.Response(response_data)

    @decorators.action(methods=["POST"], detail=True, url_path="ptz/auto-focus")
    def auto_focus(self, request, pk=None):
        camera = self.get_object()
        manager = EocortexManager()
        response_data = manager.auto_focus(camera.channel_id)
        return response.Response(response_data)

    @decorators.action(methods=["POST"], detail=True, url_path="ptz/center")
    def center_camera(self, request, pk=None):
        camera = self.get_object()
        width = request.data.get("width")
        height = request.data.get("height")
        x = request.data.get("x")
        y = request.data.get("y")
        manager = EocortexManager()
        response_data = manager.center_camera(camera.channel_id, width, height, x, y)
        return response.Response(response_data)

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


class CommandCenterViewSet(viewsets.ModelViewSet):
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ("cameras__channel_id", "cameras__location__name", "name")
    permission_classes = (IsAuthenticated, DjangoModelPermissions)
    queryset = CommandCenter.objects.filter().order_by("-created_at")
    http_method_names = ["get", "head", "options", "post", "put", "delete"]
    lookup_field = "id32"

    def get_serializer_class(self):
        if self.action in ["create", "update"]:
            return CommandCenterWriteSerializer
        return CommandCenterReadSerializer
