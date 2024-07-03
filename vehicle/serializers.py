from rest_framework import serializers
from .models import Vehicle, VehicleType, Person


class VehicleTypeSerializer(serializers.ModelSerializer):
    id32 = serializers.CharField(read_only=True)

    class Meta:
        model = VehicleType
        fields = ("id32", "name")


class VehicleSerializer(serializers.ModelSerializer):
    last_checkin = serializers.IntegerField(read_only=True)
    id32 = serializers.CharField(read_only=True)
    vehicle_type = serializers.SerializerMethodField()
    person = serializers.SerializerMethodField()

    def get_vehicle_type(self, instance):
        return VehicleTypeSerializer(instance.vehicle_type).data

    def get_person(self, instance):
        if not instance.person:
            return

        return {
            "full_name": instance.person.full_name,
            "no_id": instance.person.no_id,
            "id32": instance.person.id32,
        }

    class Meta:
        model = Vehicle
        fields = (
            "id32",
            "license_plate_number",
            "vehicle_type",
            "person",
            "last_checkin",
        )
        read_only_fields = ("full_name", "no_id", "last_checkin")


class VehicleWriteSerializer(VehicleSerializer):
    vehicle_type = serializers.CharField()
    person = serializers.CharField()

    def validate_person(self, data):
        instance = Person.objects.filter(id32=data).last()
        if not instance:
            raise serializers.ValidationError("invalid person")
        return instance

    def validate_vehicle_type(self, data):
        instance = VehicleType.objects.filter(id32=data).last()
        if not instance:
            raise serializers.ValidationError("invalid vehicle type")
        return instance

class VehicleLiteSerializer(serializers.ModelSerializer):
    vehicle_type = serializers.SerializerMethodField()

    def get_vehicle_type(self, instance):
        return VehicleTypeSerializer(instance.vehicle_type).data
    class Meta:
        model = Vehicle
        fields = ("id32", "license_plate_number", "vehicle_type")