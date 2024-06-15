from django_filters import rest_framework as django_filters
from rest_framework import viewsets, filters, decorators, response
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from libs.filter import CreatedAtFilterMixin
from libs.pagination import CustomPagination
from libs.resident import get_last_resident
from .models import Resident
from .serializers import ResidentReadSerializer, ResidentWriteSerializer


class ResidentViewSet(viewsets.ModelViewSet):
    queryset = Resident.objects.filter()
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticated, DjangoModelPermissions)
    filterset_class = CreatedAtFilterMixin
    filter_backends = (filters.SearchFilter, django_filters.DjangoFilterBackend)
    search_fields = ("full_name", "no_id", "address")
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    lookup_field = "id32"

    def get_serializer_class(self):
        if self.action in ["create", "partial_update"]:
            return ResidentWriteSerializer
        return ResidentReadSerializer

    @decorators.action(methods=["GET"], detail=False, url_path="recent")
    def get_last_resident(self, request):
        return response.Response(get_last_resident())
