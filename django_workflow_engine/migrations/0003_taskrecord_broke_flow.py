# Generated by Django 3.2.9 on 2021-11-15 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("django_workflow_engine", "0002_alter_flow_workflow_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="taskrecord",
            name="broke_flow",
            field=models.BooleanField(default=False),
        ),
    ]
