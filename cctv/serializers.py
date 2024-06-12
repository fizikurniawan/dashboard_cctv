from rest_framework import serializers
from .models import Camera
from django.conf import settings



class CameraSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        instance = self.instance
        attrs = super().validate(attrs)

        channel_id = attrs["channel_id"]
        exist_channel_id = Camera.objects.filter(channel_id=channel_id)
        if instance:
            exist_channel_id = exist_channel_id.exclude(id=instance.id)

        if exist_channel_id.exists():
            raise serializers.ValidationError(
                {"channel_id": f"{channel_id} has already exists. Pick another one"}
            )

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
        )
        read_only_fields = ("id32", "hls_url")
