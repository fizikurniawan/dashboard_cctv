from rest_framework import serializers
from .models import Camera, LPR, Location
from django.conf import settings
from vehicle.serializers import VehicleSerializer


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ("id32", "name", "description")
        read_only_fields = ("id32",)


class CameraSerializer(serializers.ModelSerializer):
    location = serializers.CharField(required=False, allow_null=True)

    def to_representation(self, instance):
        resp_dict = super().to_representation(instance)
        if instance.location:
            resp_dict["location"] = LocationSerializer(instance.location).data

        return resp_dict

    def validate(self, attrs):
        instance = self.instance
        attrs = super().validate(attrs)

        channel_id = attrs["channel_id"]
        location = attrs.get("location")
        exist_channel_id = Camera.objects.filter(channel_id=channel_id)
        if instance:
            exist_channel_id = exist_channel_id.exclude(id=instance.id)

        if exist_channel_id.exists():
            raise serializers.ValidationError(
                {"channel_id": f"{channel_id} has already exists. Pick another one"}
            )

        if location:
            location_instance = Location.objects.filter(id32=location).last()
            if not location_instance:
                raise serializers.ValidationError({"location": "invalid location"})
            attrs["location"] = location_instance

        return attrs

    class Meta:
        model = Camera
        fields = (
            "id32",
            "channel_id",
            "name",
            "description",
            "is_active",
            "order",
            "hls_url",
            "is_gate",
            "location",
        )
        read_only_fields = ("id32", "hls_url")


class LPRSerializer(serializers.ModelSerializer):
    camera = serializers.SerializerMethodField()
    vehicle = serializers.SerializerMethodField()

    def get_camera(self, instance):
        if not instance.camera:
            return
        return {"id32": instance.camera.id32, "name": instance.camera.name}

    def get_vehicle(self, instance):
        if not instance.vehicle:
            return
        return VehicleSerializer(instance.vehicle).data

    class Meta:
        model = LPR
        fields = "__all__"
