# Generated by Django 4.2.3 on 2024-06-14 15:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("vehicle", "0003_remove_vehicle_code_remove_vehicle_owner_contact_and_more"),
        ("cctv", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="camera",
            name="is_gate",
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name="LPR",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("number_plate", models.CharField(max_length=100)),
                (
                    "direction",
                    models.CharField(
                        choices=[("in", "IN"), ("out", "OUT"), ("unknown", "UNKNOWN")],
                        max_length=20,
                    ),
                ),
                ("time_utc_timestamp", models.BigIntegerField()),
                (
                    "vehicle",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="vehicle.vehicle",
                    ),
                ),
            ],
        ),
    ]
