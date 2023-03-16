from django.db import migrations


def data_migration_on_all_models(apps, schema_editor):
    """
    Run a simple data migration on all models in the database.
    """
    Flow = apps.get_model("django_workflow_engine", "Flow")
    Flow.objects.all().count()

    TaskRecord = apps.get_model("django_workflow_engine", "TaskRecord")
    TaskRecord.objects.all().count()

    Target = apps.get_model("django_workflow_engine", "Target")
    Target.objects.all().count()

    TaskLog = apps.get_model("django_workflow_engine", "TaskLog")
    TaskLog.objects.all().count()


class Migration(migrations.Migration):

    initial = True
    dependencies = [
        ("django_workflow_engine", "0007_flow_running"),
    ]
    run_before = [
        ("django_workflow_engine", "0008_remove_taskrecord_broke_flow"),
    ]

    operations = [
        migrations.RunPython(data_migration_on_all_models, migrations.RunPython.noop),
    ]
