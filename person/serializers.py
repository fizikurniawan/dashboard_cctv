import base64
from rest_framework import serializers
from person.models import Person
from common.serializers import FileLiteSerializer, File
from vehicle.models import Vehicle, VehicleType
from activity.models import CheckIn
from time import time
from libs.eocortex import EocortexManager
from django.core.files.base import ContentFile
from libs.utils import detect_image_type
from libs.exception import EocortexFailedFR


class VehicleLiteSerializer(serializers.ModelSerializer):
    vehicle_type = serializers.CharField()

    def validate_vehicle_type(self, data):
        instance = VehicleType.objects.filter(id32=data).last()
        if not instance:
            raise serializers.ValidationError("invalid vehicle type")
        return instance

    class Meta:
        model = Vehicle
        fields = ("license_plate_number", "vehicle_type")


class PersonReadSerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField()

    def get_photo(self, instance):
        if not instance.photo:
            return

        return FileLiteSerializer(instance.photo).data

    def to_representation(self, instance):
        resp_dict = super().to_representation(instance)

        return {
            **resp_dict,
            "gender": instance.gender_dict,
            "doc_type": instance.doc_type_dict,
        }

    class Meta:
        model = Person
        fields = ("id32", "no_id", "full_name", "address", "photo", "person_type")


class PersonWriteSerializer(serializers.ModelSerializer):
    vehicle = VehicleLiteSerializer()
    person = serializers.CharField(required=False, allow_null=True)
    person_type = serializers.CharField()
    purpose_of_visit = serializers.CharField(required=False, allow_null=True)
    camera_photo_base64 = serializers.CharField(required=False, allow_null=True)
    allow_fail_eocortex = serializers.BooleanField(default=True)

    def validate_person(self, data):
        if not data:
            return
        person_instance = Person.objects.filter(id32=data).last()
        if not person_instance:
            raise serializers.ValidationError("invalid person")
        return person_instance

    def validate(self, attrs):
        if attrs["person_type"] != Person.VISITOR:
            return super().validate(attrs)

        # camera_photo_base64 and purpose_of_visit is required for VISITOR
        errors = {}
        if not attrs.get("purpose_of_visit"):
            errors["purpose_of_visit"] = ["this field is required"]

        if not attrs.get("camera_photo_base64"):
            errors["camera_photo_base64"] = ["this field is required"]

        if errors:
            raise serializers.ValidationError(errors)

        ext = detect_image_type(attrs["camera_photo_base64"])
        if ext not in ["png", "jpg"]:
            raise serializers.ValidationError(
                {
                    "camera_photo_base64": [
                        "invalid format photo. format should be png or jpg"
                    ]
                }
            )

        return super().validate(attrs)

    def create(self, validated_data):
        person = validated_data.pop("person", None)
        vehicle = validated_data.pop("vehicle")
        person_type = validated_data.get("person_type", None)
        purpose_of_visit = validated_data.pop("purpose_of_visit", None)
        camera_photo_base64 = validated_data.pop("camera_photo_base64", None)
        allow_fail_eocortex = validated_data.pop("allow_fail_eocortex", False)

        if not person:
            person = Person.objects.filter(no_id=validated_data["no_id"]).first()

        if not person:
            person = Person.objects.create(**validated_data)
        else:
            # update person data
            for column in ["full_name", "address", "gender", "doc_type", "person_type"]:
                setattr(person, column, validated_data.get(column))
            person.save()

        # get vehicle
        vehicle_instance, _ = Vehicle.objects.get_or_create(**vehicle, person=person)

        # create activity check in if user_type is visitor
        if person_type and person_type == Person.VISITOR:
            check_in = CheckIn.objects.create(
                person=person,
                check_in_timestamp=int(time() * 1000),
                vehicle=vehicle_instance,
                purpose_of_visit=purpose_of_visit,
            )

            ext = detect_image_type(camera_photo_base64)
            file_name = f"camera_photo_of_checkin_{check_in.id32}.{ext}"
            file_data = ContentFile(
                base64.b64decode(camera_photo_base64), name=file_name
            )
            file_instance = File.objects.create(file=file_data, name=file_name)

            # let's submit eocortext facerecog
            em = EocortexManager()
            is_success, response = em.submit_img_to_face_reg(
                camera_photo_base64, person
            )
            if not is_success and not allow_fail_eocortex:
                raise EocortexFailedFR(response.get("ErrorMessage", str(response)))

            check_in.camera_photo = file_instance
            check_in.save()

        return person

    class Meta:
        model = Person
        fields = (
            "id32",
            "no_id",
            "full_name",
            "address",
            "gender",
            "doc_type",
            "vehicle",
            "person_type",
            "person",
            "created_at",
            "purpose_of_visit",
            "camera_photo_base64",
            "allow_fail_eocortex",
        )
        write_only_fields = ("vehicle", "person", "purpose_of_visit")
        read_only_fields = ("id32", "created_at")
