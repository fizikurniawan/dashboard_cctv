from django_filters import rest_framework as django_filters
from rest_framework import viewsets, filters, decorators, response
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from libs.filter import CreatedAtFilterMixin
from libs.pagination import CustomPagination
from libs.person import get_last_person
from .models import Person
from .serializers import PersonReadSerializer, PersonWriteSerializer
from django.core.files.base import ContentFile
import base64
from common.models import File
from common.serializers import FileLiteSerializer
from vehicle.models import Vehicle


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.filter()
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticated, DjangoModelPermissions)
    filterset_class = CreatedAtFilterMixin
    filter_backends = (filters.SearchFilter, django_filters.DjangoFilterBackend)
    search_fields = ("full_name", "no_id", "address")
    http_method_names = ["get", "post", "put", "delete", "head", "options"]
    lookup_field = "id32"

    def get_serializer_class(self):
        if self.action in ["create", "partial_update"]:
            return PersonWriteSerializer
        return PersonReadSerializer

    @decorators.action(methods=["GET"], detail=False, url_path="recent")
    def get_last_person(self, request):
        person_dict = get_last_person()
        photo = person_dict.pop("photo", None)
        if photo:
            file_name = f"photo_of_{person_dict['full_name']}.jpeg"
            file_data = ContentFile(base64.b64decode(photo), name=file_name)
            file_instance = File.objects.create(file=file_data, name=file_name)
            person_dict["photo"] = FileLiteSerializer(file_instance).data
        else:
            person_dict["photo"] = None

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
        person_dict["gender"] = gender_dict.get(person_dict["gender"])

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
        person_dict["doc_type"] = doc_type_dict.get(person_dict["doc_type"])

        # get or create resident by no_id
        resident = Person.objects.filter(no_id=person_dict["no_id"]).first()
        if not resident:
            resident_create_kwargs = person_dict
            resident_create_kwargs["photo"] = file_instance
            resident = Person.objects.create(**person_dict)

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
        person_dict["resident"] = {
            "id32": resident.id32,
            "full_name": resident.full_name,
        }
        person_dict["vehicles"] = vehicle_dict

        return response.Response(person_dict)
