# Generated by Django 4.0.3 on 2022-03-07 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("django_workflow_engine", "0005_rename_finished_at_taskrecord_executed_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="taskrecord",
            name="done",
            field=models.BooleanField(default=False),
        ),
    ]
