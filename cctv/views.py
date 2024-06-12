from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from libs.pagination import CustomPagination
from .models import Camera
from .serializers import CameraSerializer


class CameraViewSet(viewsets.ModelViewSet):
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name", "channel_id")
    permission_classes = (IsAuthenticated, DjangoModelPermissions)
    queryset = Camera.objects.filter()
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    serializer_class = CameraSerializer
    lookup_field = "id32"
