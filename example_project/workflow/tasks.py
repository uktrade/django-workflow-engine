from django_workflow_engine.tasks import Task


class LogMessageTask(Task):
    auto = False
    task_name = "log_message"

    def execute(self, task_info):
        print(task_info["message"])
