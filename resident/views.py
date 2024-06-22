from django_filters import rest_framework as django_filters
from rest_framework import viewsets, filters, decorators, response
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from libs.filter import CreatedAtFilterMixin
from libs.pagination import CustomPagination
from libs.resident import get_last_resident
from .models import Resident
from .serializers import ResidentReadSerializer, ResidentWriteSerializer
from django.core.files.base import ContentFile
import base64
from common.models import File
from common.serializers import FileLiteSerializer


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
        resident_dict = get_last_resident()
        photo = resident_dict.pop("photo", None)
        if photo:
            file_name = f"photo_of_{resident_dict['full_name']}.jpeg"
            file_data = ContentFile(base64.b64decode(photo), name=f"temp.image/jpeg")
            file_instance = File.objects.create(file=file_data, name=file_name)
            resident_dict["photo"] = FileLiteSerializer(file_instance).data
        else:
            resident_dict["photo"] = None

        return response.Response(resident_dict)
