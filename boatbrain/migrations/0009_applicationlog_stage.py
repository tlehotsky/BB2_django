# Generated by Django 5.0 on 2025-02-18 01:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boatbrain', '0008_alter_bbtriplog_trip_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='applicationlog',
            name='stage',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
