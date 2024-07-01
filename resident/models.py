from django.db import models
from django.utils.translation import gettext_lazy as _
from common.models import File
from libs.base_model import BaseModelGeneric


class Resident(BaseModelGeneric):
    GENDER_CHOICES = (
        (0, "Male"),
        (1, "Female"),
    )
    DOC_TYPE_CHOICES = (
        ("DL", "Daily Pass"),
        ("ML", "Monthly Pass"),
        ("WL", "Weekly Pass"),
    )

    no_id = models.CharField(max_length=250)
    full_name = models.CharField(max_length=250)
    gender = models.IntegerField(choices=GENDER_CHOICES)
    address = models.TextField()
    photo = models.ForeignKey(File, on_delete=models.SET_NULL, null=True, blank=True)
    doc_type = models.CharField(max_length=10, choices=DOC_TYPE_CHOICES)

    def __str__(self):
        return f"{self.no_id} - {self.full_name}"

    @property
    def gender_dict(self):
        return {"value": self.gender, "text": self.GENDER_CHOICES[self.gender][-1]}

    @property
    def doc_type_dict(self):
        return {
            "value": self.doc_type,
            "text": dict(self.DOC_TYPE_CHOICES).get(self.doc_type, ""),
        }

    class Meta:
        verbose_name = _("Resident")
        verbose_name_plural = _("Residents")


class Visitor(BaseModelGeneric):
    CHECK_IN = "check_in"
    CHECK_OUT = "check_out"
    GENDER_CHOICES = (
        (0, "Male"),
        (1, "Female"),
    )
    DOC_TYPE_CHOICES = (
        ("DL", "Daily Pass"),
        ("ML", "Monthly Pass"),
        ("WL", "Weekly Pass"),
    )

    ACTIVITY_TYPE = (
        (CHECK_IN, "Check In"),
        (CHECK_OUT, "Check Out"),
    )

    activity = models.CharField(max_length=50, choices=ACTIVITY_TYPE)
    resident = models.ForeignKey(
        Resident, null=True, blank=True, on_delete=models.SET_NULL
    )

    # duplicate from resident
    no_id = models.CharField(max_length=250)
    full_name = models.CharField(max_length=250)
    gender = models.IntegerField(choices=GENDER_CHOICES)
    address = models.TextField()
    photo = models.ForeignKey(File, on_delete=models.SET_NULL, null=True, blank=True)
    doc_type = models.CharField(max_length=10, choices=DOC_TYPE_CHOICES)
    vehicle = models.ForeignKey(
        "vehicle.Vehicle",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_vehicle",
    )

    def __str__(self):
        return f"{self.no_id} - {self.full_name}"

    @property
    def gender_dict(self):
        return {"value": self.gender, "text": self.GENDER_CHOICES[self.gender][-1]}

    @property
    def doc_type_dict(self):
        return {
            "value": self.doc_type,
            "text": dict(self.DOC_TYPE_CHOICES).get(self.doc_type, ""),
        }

    class Meta:
        verbose_name = _("Visitor")
        verbose_name_plural = _("Visitors")
