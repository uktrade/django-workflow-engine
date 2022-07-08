import os

from django.core.management.base import (
    BaseCommand,
    CommandError,
)

from django_workflow_engine.import_bpmn import import_BPMN

class Command(BaseCommand):
    help = "IMport a valid BPMN file and create the Python workflow file"

    def add_arguments(self, parser):
        parser.add_argument("bpmn_path")
        parser.add_argument("workflow_name")
        parser.add_argument("python_path")

    def handle(self, *args, **options):
        bpmn_path = options["bpmn_path"]
        python_path = options["python_path"]
        workflow_name = options["workflow_name"]

        import_BPMN(bpmn_path, workflow_name, python_path)

