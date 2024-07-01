from django_filters import rest_framework as django_filters
from rest_framework import viewsets, filters, decorators, response
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from libs.filter import CreatedAtFilterMixin
from libs.pagination import CustomPagination
from libs.resident import get_last_resident
from .models import Resident, Visitor
from .serializers import (
    ResidentReadSerializer,
    ResidentWriteSerializer,
    VisitorSerializer,
)
from django.core.files.base import ContentFile
import base64
from common.models import File
from common.serializers import FileLiteSerializer
from vehicle.models import Vehicle


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
            file_data = ContentFile(base64.b64decode(photo), name=file_name)
            file_instance = File.objects.create(file=file_data, name=file_name)
            resident_dict["photo"] = FileLiteSerializer(file_instance).data
        else:
            resident_dict["photo"] = None

        gender_dict = {
            0: {
                "value": 0,
                "text": "Male",
            },
            1: {
                "value": 1,
                "text": "Female",
            },
        }
        resident_dict["gender"] = gender_dict.get(resident_dict["gender"])

        doc_type_dict = {
            "DL": {
                "value": "DL",
                "text": "Daily Pass",
            },
            "ML": {
                "value": "ML",
                "text": "Monthly Pass",
            },
        }
        resident_dict["doc_type"] = doc_type_dict.get(resident_dict["doc_type"])

        # get or create resident by no_id
        resident = Resident.objects.filter(no_id=resident_dict["no_id"]).first()
        if not resident:
            resident_create_kwargs = resident_dict
            resident_create_kwargs["photo"] = file_instance
            resident = Resident.objects.create(**resident_dict)

        vehicles = Vehicle.objects.filter(owner=resident)
        vehicle_dict = [
            {
                "id32": vehicle.id32,
                "license_plate_number": vehicle.license_plate_number,
                "vehicle_type": {
                    "id32": vehicle.vehicle_type.id32,
                    "name": vehicle.vehicle_type.name,
                },
            }
            for vehicle in vehicles
        ]
        resident_dict["resident"] = {
            "id32": resident.id32,
            "full_name": resident.full_name,
        }
        resident_dict["vehicles"] = vehicle_dict

        return response.Response(resident_dict)


class VisitorViewSet(viewsets.ModelViewSet):
    queryset = Visitor.objects.filter().order_by("-created_at")
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticated, DjangoModelPermissions)
    filterset_class = CreatedAtFilterMixin
    filter_backends = (filters.SearchFilter, django_filters.DjangoFilterBackend)
    search_fields = ("full_name", "no_id", "address")
    http_method_names = ["get", "post", "head", "options"]
    lookup_field = "id32"
    serializer_class = VisitorSerializer
