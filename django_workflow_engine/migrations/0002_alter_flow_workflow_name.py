# Generated by Django 3.2.7 on 2021-10-04 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("django_workflow_engine", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="flow",
            name="workflow_name",
            field=models.CharField(max_length=255, verbose_name="Select workflow"),
        ),
    ]
