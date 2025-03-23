# Generated by Django 5.0 on 2025-02-18 01:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boatbrain', '0007_bbtriplog_trip_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bbtriplog',
            name='trip_type',
            field=models.CharField(blank=True, choices=[('REAL', 'Real Trip'), ('TEST', 'Test Data')], db_index=True, default='REAL', max_length=10, null=True),
        ),
    ]
