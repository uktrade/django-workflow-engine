from django.core.management.base import BaseCommand

from django_workflow_engine.models import Flow


class Command(BaseCommand):
    help = "Clean up duplicate TaskRecords"

    def handle(self, *args, **options):
        self.stdout.write("Cleaning up duplicate TaskRecords...")
        unfinished_flows = Flow.objects.filter(finished__isnull=True)
        for flow in unfinished_flows:
            unexecuted_tasks = flow.tasks.filter(executed_at__isnull=True)
            steps_running = []
            for task in unexecuted_tasks:
                if task.step_id in steps_running:
                    task.delete()
                    self.stdout.write(
                        "Deleted duplicate TaskRecord for Flow "
                        f"{flow.pk} and step {task.step_id}"
                    )
                else:
                    steps_running.append(task.step_id)
        self.stdout.write("Done.")
