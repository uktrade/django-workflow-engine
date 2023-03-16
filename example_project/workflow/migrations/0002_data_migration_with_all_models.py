from django.db import migrations


def data_migration_on_all_models(apps, schema_editor):
    """
    Run a simple data migration on all models in the database.
    """
    Flow = apps.get_model("django_workflow_engine", "Flow")
    Flow.objects.all().count()

    TaskStatus = apps.get_model("django_workflow_engine", "TaskStatus")
    TaskStatus.objects.all().count()

    Target = apps.get_model("django_workflow_engine", "Target")
    Target.objects.all().count()

    TaskLog = apps.get_model("django_workflow_engine", "TaskLog")
    TaskLog.objects.all().count()

    TaskRecordExecution = apps.get_model(
        "django_workflow_engine", "TaskRecordExecution"
    )
    TaskRecordExecution.objects.all().count()


class Migration(migrations.Migration):

    initial = True
    dependencies = [
        ("django_workflow_engine", "0011_migrate_from_taskrecordexecutions"),
        ("workflow", "0001_data_migration_with_all_models"),
    ]

    operations = [
        migrations.RunPython(data_migration_on_all_models, migrations.RunPython.noop),
    ]
