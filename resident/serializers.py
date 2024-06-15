from rest_framework import serializers
from resident.models import Resident
from common.serializers import FileLiteSerializer


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
