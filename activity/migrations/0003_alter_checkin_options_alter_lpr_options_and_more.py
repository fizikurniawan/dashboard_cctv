# Generated by Django 4.2.3 on 2024-07-04 11:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("activity", "0002_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="checkin",
            options={
                "ordering": ("-updated_at",),
                "verbose_name": "CheckIn",
                "verbose_name_plural": "CheckIns",
            },
        ),
        migrations.AlterModelOptions(
            name="lpr",
            options={
                "ordering": ("-time_utc_timestamp",),
                "verbose_name": "LPR",
                "verbose_name_plural": "LPRs",
            },
        ),
        migrations.AddField(
            model_name="checkin",
            name="purpose_of_visit",
            field=models.CharField(
                choices=[
                    ("rapat", "Rapat"),
                    ("melakukan-pekerjaan", "Melakukan Pekerjaan"),
                    ("berkunjung", "Berkunjung"),
                    ("patroli", "Patroli"),
                ],
                default="berkunjung",
                max_length=50,
            ),
        ),
    ]