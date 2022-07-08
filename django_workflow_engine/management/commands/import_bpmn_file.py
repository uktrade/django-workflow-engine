from django.core.management.base import (
    BaseCommand,
)

from django_workflow_engine.import_bpmn import import_BPMN


class Command(BaseCommand):
    help = "Import a valid BPMN file and create the Python workflow file"

    def add_arguments(self, parser):
        parser.add_argument("bpmn_path")
        parser.add_argument("python_path")

    def handle(self, *args, **options):
        bpmn_path = options["bpmn_path"]
        python_path = options["python_path"]

        import_BPMN(bpmn_path, python_path)
