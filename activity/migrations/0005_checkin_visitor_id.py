# Generated by Django 4.2.3 on 2024-08-18 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("activity", "0004_lpr_snapshot"),
    ]

    operations = [
        migrations.AddField(
            model_name="checkin",
            name="visitor_id",
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
    ]
