from rest_framework import serializers
from .models import Vehicle, VehicleType


class VehicleTypeSerializer(serializers.ModelSerializer):
    id32 = serializers.CharField(read_only=True)
    class Meta:
        model = VehicleType
        fields = ("id32", "name")


class VehicleSerializer(serializers.ModelSerializer):
    id32 = serializers.CharField(read_only=True)
    vehicle_type = serializers.SerializerMethodField()

    def get_vehicle_type(self, instance):
        return VehicleTypeSerializer(instance.vehicle_type).data

    class Meta:
        model = Vehicle
        fields = (
            "id32",
            "license_plate_number",
            "vehicle_type",
            "owner_full_name",
            "owner_contact",
            "code",
        )


class VehicleWriteSerializer(VehicleSerializer):
    vehicle_type = serializers.CharField()

    def validate_vehicle_type(self, data):
        instance = VehicleType.objects.filter(id32=data).last()
        if not instance:
            raise serializers.ValidationError("invalid vehicle type")
        return instance
