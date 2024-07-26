from rest_framework import serializers
from vehicle.serializers import VehicleSerializer, VehicleLiteSerializer
from .models import LPR, CheckIn
from person.serializers import PersonReadSerializer
from django.shortcuts import get_object_or_404
from time import time
from common.serializers import FileLiteSerializer


class LPRSerializer(serializers.ModelSerializer):
    camera = serializers.SerializerMethodField()
    vehicle = serializers.SerializerMethodField()
    snapshot = serializers.SerializerMethodField()

    def get_camera(self, instance):
        if not instance.camera:
            return
        return {"id32": instance.camera.id32, "name": instance.camera.name}

    def get_vehicle(self, instance):
        if not instance.vehicle:
            return
        return VehicleSerializer(instance.vehicle).data

    def get_snapshot(self, instance):
        if not instance.snapshot:
            return
        return FileLiteSerializer(instance.snapshot).data

    class Meta:
        model = LPR
        fields = "__all__"


class CheckInSerializer(serializers.ModelSerializer):
    person = serializers.SerializerMethodField()
    vehicle = serializers.SerializerMethodField()
    purpose_of_visit = serializers.SerializerMethodField()

    def get_person(self, instance):
        if not instance.person:
            return
        return PersonReadSerializer(instance.person).data

    def get_vehicle(self, instance):
        if not instance.vehicle:
            return
        return VehicleLiteSerializer(instance.vehicle).data

    def get_purpose_of_visit(self, instance):
        return instance.purpose_of_visit_dict

    class Meta:
        model = CheckIn
        fields = (
            "id32",
            "person",
            "check_in_timestamp",
            "check_out_timestamp",
            "vehicle",
            "purpose_of_visit",
        )


class CheckOutSerializer(serializers.Serializer):
    check_in = serializers.CharField(write_only=True)

    def validate_check_in(self, data):
        instance = get_object_or_404(
            CheckIn, id32=data, check_out_timestamp__isnull=True
        )

        return instance

    def create(self, validated_data):
        check_in = validated_data.pop("check_in", None)
        check_in.check_out_timestamp = int(time() * 1000)
        check_in.save()

        return check_in
