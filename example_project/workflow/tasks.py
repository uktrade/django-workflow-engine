from django_workflow_engine.tasks import Task


class LogMessageTask(Task):
    auto = True
    task_name = "log_message"

    def execute(self, task_info):
        print(task_info["message"])

        return [], True
