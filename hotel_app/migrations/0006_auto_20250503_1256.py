# Generated by Django 3.1.7 on 2025-05-03 07:26

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('hotel_app', '0005_auto_20250503_1246'),
    ]

    operations = [
        migrations.AddField(
            model_name='maintenanceassignment',
            name='createdAt',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='maintenanceassignment',
            name='createdBy',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_assignments', to='hotel_app.user'),
        ),
        migrations.AddField(
            model_name='maintenanceassignment',
            name='updatedAt',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='maintenanceassignment',
            name='updatedBy',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_assignments', to='hotel_app.user'),
        ),
        migrations.AddField(
            model_name='maintenancerequest',
            name='createdAt',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='maintenancerequest',
            name='createdBy',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_maintenance_requests', to='hotel_app.user'),
        ),
        migrations.AddField(
            model_name='maintenancerequest',
            name='updatedAt',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='maintenancerequest',
            name='updatedBy',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_maintenance_requests', to='hotel_app.user'),
        ),
    ]
