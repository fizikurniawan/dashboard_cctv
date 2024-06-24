from rest_framework import serializers
from .models import Camera, LPR, Location, CommandCenter
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


class CommandCenterReadSerializer(serializers.ModelSerializer):
    cameras = serializers.SerializerMethodField()

    def get_cameras(self, instance):
        queryset = instance.cameras.filter()
        if not queryset.exists():
            return

        return CameraSerializer(queryset, many=True).data

    class Meta:
        model = CommandCenter
        fields = ("id32", "name", "cameras")


class CommandCenterWriteSerializer(serializers.ModelSerializer):
    cameras = serializers.ListSerializer(child=serializers.CharField())

    def validate_cameras(self, data):
        camera_instances = Camera.objects.filter(id32__in=data)
        if not camera_instances.exists():
            raise serializers.ValidationError("Invalid camera id32s")
        return camera_instances

    def validate_name(self, data):
        instance = self.instance
        exists_name = CommandCenter.objects.filter(name=data)
        if instance:
            exists_name = exists_name.exclude(id=instance.id)
        if exists_name.exists():
            raise serializers.ValidationError(
                "Name has already exists. Pick another one"
            )
        return data

    def create(self, validated_data):
        cameras = validated_data.pop("cameras", [])
        camera_instance = CommandCenter.objects.create(name=validated_data["name"])
        camera_instance.cameras.set(cameras)

        return camera_instance

    def update(self, instance, validated_data):
        cameras = validated_data.pop("cameras", [])
        instance.name = validated_data["name"]
        instance.cameras.set(cameras)

        return instance

    class Meta:
        model = CommandCenter
        fields = ("id32", "name", "cameras")
        read_only_fields = ("id32", )
