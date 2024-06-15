from rest_framework import serializers
from .models import Vehicle, VehicleType, Resident


class VehicleTypeSerializer(serializers.ModelSerializer):
    id32 = serializers.CharField(read_only=True)

    class Meta:
        model = VehicleType
        fields = ("id32", "name")


class VehicleSerializer(serializers.ModelSerializer):
    id32 = serializers.CharField(read_only=True)
    vehicle_type = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()

    def get_vehicle_type(self, instance):
        return VehicleTypeSerializer(instance.vehicle_type).data

    def get_owner(self, instance):
        if not instance.owner:
            return
        
        return {
            "full_name": instance.owner.full_name,
            "no_id": instance.owner.no_id,
            "id32": instance.owner.id32,
        }

    class Meta:
        model = Vehicle
        fields = ("id32", "license_plate_number", "vehicle_type", "owner")
        read_only_fields = ("full_name", "no_id")


class VehicleWriteSerializer(VehicleSerializer):
    vehicle_type = serializers.CharField()
    owner = serializers.CharField()

    def validate_owner(self, data):
        instance = Resident.objects.filter(id32=data).last()
        if not instance:
            raise serializers.ValidationError("invalid owner")
        return instance

    def validate_vehicle_type(self, data):
        instance = VehicleType.objects.filter(id32=data).last()
        if not instance:
            raise serializers.ValidationError("invalid vehicle type")
        return instance
