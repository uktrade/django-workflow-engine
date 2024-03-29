# Generated by Django 3.2.9 on 2021-11-16 08:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("django_workflow_engine", "0003_taskrecord_broke_flow"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="taskrecord",
            name="target",
        ),
        migrations.CreateModel(
            name="Target",
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
                (
                    "target_string",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                (
                    "task_record",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="targets",
                        to="django_workflow_engine.taskrecord",
                    ),
                ),
            ],
        ),
    ]
