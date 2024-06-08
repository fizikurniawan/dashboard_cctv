from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from libs.base_model import BaseModelGeneric
from libs.storage import FILE_STORAGE


class File(BaseModelGeneric):
    name = models.CharField(max_length=255)
    file = models.FileField(storage=FILE_STORAGE, max_length=300, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, blank=True, null=True
    )
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        return "%s - %s" % (self.name, self.file)

    def get_file(self):
        if self.file:
            return self.file.url
        return None

    class Meta:
        verbose_name = _("File")
        verbose_name_plural = _("Files")


class Configuration(models.Model):
    key = models.CharField(
        max_length=255, unique=True, help_text="The name of the configuration setting"
    )
    value = models.TextField(help_text="The value of the configuration setting")
    description = models.TextField(
        blank=True, null=True, help_text="The description of the configuration setting"
    )

    def __str__(self):
        return f"{self.key}: {self.value}"

    class Meta:
        verbose_name = "Configuration"
        verbose_name_plural = "Configurations"
