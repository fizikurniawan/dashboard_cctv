# Generated by Django 4.2.3 on 2024-06-14 15:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("resident", "0001_initial"),
        ("vehicle", "0002_alter_vehicle_license_plate_number_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="vehicle",
            name="code",
        ),
        migrations.RemoveField(
            model_name="vehicle",
            name="owner_contact",
        ),
        migrations.RemoveField(
            model_name="vehicle",
            name="owner_full_name",
        ),
        migrations.AddField(
            model_name="vehicle",
            name="owner",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="resident.resident",
            ),
        ),
    ]
