from rest_framework import serializers
from person.models import Person
from common.serializers import FileLiteSerializer
from vehicle.models import Vehicle, VehicleType
from activity.models import CheckIn
from time import time


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

    def validate_person(self, data):
        if not data:
            return
        person_instance = Person.objects.filter(id32=data).last()
        if not person_instance:
            raise serializers.ValidationError("invalid person")
        return person_instance

    def create(self, validated_data):
        person = validated_data.pop("person", None)
        vehicle = validated_data.pop("vehicle")
        person_type = validated_data.get("person_type", None)

        if not person:
            person = Person.objects.filter(no_id=validated_data["no_id"]).first()
        else:
            # update person data
            for column in ["full_name", "address", "gender", "doc_type"]:
                setattr(person, column, validated_data.get(column))
            person.save()

        if not person:
            person = Person.objects.create(**validated_data)

        # get vehicle
        vehicle_instance, _ = Vehicle.objects.get_or_create(**vehicle, person=person)

        # create activity check in if user_type is visitor
        if person_type and person_type == Person.VISITOR:
            CheckIn.objects.create(
                person=person,
                check_in_timestamp=int(time() * 1000),
                vehicle=vehicle_instance,
            )

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
        )
        write_only_fields = ("vehicle", "person")
        read_only_fields = ("id32", "created_at")
