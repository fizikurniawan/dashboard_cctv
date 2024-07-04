from django.db import models
from libs.base_model import BaseModelGeneric
from common.models import File
from django.utils.translation import gettext_lazy as _


class Person(BaseModelGeneric):
    GENDER_CHOICES = (
        (0, "Male"),
        (1, "Female"),
    )
    DOC_TYPE_CHOICES = (
        ("DL", "Daily Pass"),
        ("ML", "Monthly Pass"),
        ("WL", "Weekly Pass"),
    )

    VISITOR = "visitor"
    RESIDENT = "resident"
    PERSON_TYPE_CHOICES = (
        (RESIDENT, "Resident"),
        (VISITOR, "Visitor"),
    )

    no_id = models.CharField(max_length=250)
    full_name = models.CharField(max_length=250)
    gender = models.IntegerField(choices=GENDER_CHOICES)
    address = models.TextField()
    photo = models.ForeignKey(File, on_delete=models.SET_NULL, null=True, blank=True)
    doc_type = models.CharField(
        max_length=10, choices=DOC_TYPE_CHOICES, null=True, blank=True
    )
    person_type = models.CharField(
        max_length=10, choices=PERSON_TYPE_CHOICES, null=True, blank=True
    )
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
        if not self.doc_type:
            return
        return {
            "value": self.doc_type,
            "text": dict(self.DOC_TYPE_CHOICES).get(self.doc_type, ""),
        }

    class Meta:
        verbose_name = _("Person")
        verbose_name_plural = _("People")
