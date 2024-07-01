from rest_framework import serializers
from resident.models import Resident, Visitor
from common.serializers import FileLiteSerializer
from vehicle.models import Vehicle, VehicleType


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


class ResidentReadSerializer(serializers.ModelSerializer):
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
        model = Resident
        fields = ("id32", "no_id", "full_name", "address", "photo")


class ResidentWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Resident
        fields = (
            "id32",
            "no_id",
            "full_name",
            "address",
            "photo",
            "gender",
            "doc_type",
        )


class VisitorSerializer(serializers.ModelSerializer):
    vehicle = VehicleLiteSerializer()
    resident = serializers.CharField(required=False, allow_null=True)

    def validate_resident(self, data):
        if not data:
            return
        resident_instance = Resident.objects.filter(id32=data).last()
        if not resident_instance:
            raise serializers.ValidationError("invalid resident")
        return resident_instance

    def to_representation(self, instance):
        resp_dict = super().to_representation(instance)
        resident = instance.resident
        resident_dict = {}
        if resident:
            resident_dict = {"id32": resident.id32, "full_name": resident.full_name}

        vehicle_dict = {}
        vehicle = instance.vehicle
        if vehicle:
            vehicle_dict = {
                "id32": vehicle.id32,
                "license_plate_number": vehicle.license_plate_number,
                "vehicle_type": {
                    "id32": vehicle.vehicle_type.id32,
                    "name": vehicle.vehicle_type.name,
                },
            }

        return {
            **resp_dict,
            "resident": resident_dict,
            "vehicle": vehicle_dict,
            "gender": instance.gender_dict,
            "doc_type": instance.doc_type_dict,
        }

    def create(self, validated_data):
        resident = validated_data.pop("resident", None)
        vehicle = validated_data.pop("vehicle")
        activity = validated_data.pop("activity")

        if not resident:
            resident = Resident.objects.filter(no_id=validated_data["no_id"])

        if not resident:
            resident = Resident.objects.create(**validated_data)

        # get vehicle
        vehicle_instance, _ = Vehicle.objects.get_or_create(**vehicle, owner=resident)

        # create visitor
        visitor = Visitor.objects.create(
            **validated_data,
            vehicle=vehicle_instance,
            resident=resident,
            activity=activity
        )

        return visitor

    class Meta:
        model = Visitor
        fields = (
            "id32",
            "no_id",
            "full_name",
            "address",
            "gender",
            "doc_type",
            "vehicle",
            "activity",
            "resident",
            "created_at",
        )
        write_only_fields = ("vehicle", "resident")
        read_only_fields = ("id32", "created_at")
