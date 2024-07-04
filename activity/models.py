from django.db import models
from libs.base_model import BaseModelGeneric
from cctv.models import Camera
from vehicle.models import Vehicle, Person
from uuid import uuid4
from django.utils.translation import gettext_lazy as _


class CheckIn(BaseModelGeneric):
    PURPOSE_OF_VISIT_CHOICES = (
        ("rapat", "Rapat"),
        ("melakukan-pekerjaan", "Melakukan Pekerjaan"),
        ("berkunjung", "Berkunjung"),
        ("patroli", "Patroli"),
    )
    person = models.ForeignKey(
        Person,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_person",
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_vehicle",
    )
    check_in_timestamp = models.BigIntegerField()
    check_out_timestamp = models.BigIntegerField(null=True, blank=True)
    purpose_of_visit = models.CharField(
        choices=PURPOSE_OF_VISIT_CHOICES, max_length=50, default="berkunjung"
    )

    @property
    def purpose_of_visit_dict(self):
        return {
            "value": self.purpose_of_visit,
            "text": dict(self.PURPOSE_OF_VISIT_CHOICES).get(
                self.purpose_of_visit, self.purpose_of_visit
            ),
        }

    class Meta:
        verbose_name = _("CheckIn")
        verbose_name_plural = _("CheckIns")
        ordering = ("-updated_at",)


class LPR(models.Model):
    DIRECTION_CHOICES = (("in", "IN"), ("out", "OUT"), ("unknown", "UNKNOWN"))
    uuid = models.UUIDField(default=uuid4, editable=False)
    channel_id = models.CharField(max_length=100)
    camera = models.ForeignKey(
        Camera,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_camera",
    )
    number_plate = models.CharField(max_length=100)
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_vehicle",
    )
    direction = models.CharField(choices=DIRECTION_CHOICES, max_length=20)
    time_utc_timestamp = models.BigIntegerField()

    def __str__(self):
        return f"{self.channel_id} - {self.number_plate} - {self.direction} - {self.time_utc_str}"

    @property
    def doc_type_dict(self):
        return {
            "value": self.doc_type,
            "text": dict(self.DOC_TYPE_CHOICES).get(self.doc_type, ""),
        }

    @property
    def full_name(self):
        if not self.vehicle:
            return
        return self.vehicle.owner.full_name

    @property
    def no_id(self):
        if not self.vehicle:
            return
        return self.vehicle.owner.no_id

    @property
    def time_utc_str(self):
        from libs.moment import convert_timestamp_ms_to_date

        return convert_timestamp_ms_to_date(self.time_utc_timestamp)

    class Meta:
        verbose_name = _("LPR")
        verbose_name_plural = _("LPRs")
        ordering = ("-time_utc_timestamp",)
