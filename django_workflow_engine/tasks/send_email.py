from django.core.mail import send_mail
from django.template import Context, Template

from .task import Task


class SendEmail(Task):
    auto = True
    task_name = "send_email"

    def execute(self, task_info):
        email_info = self.task_status.task_info | task_info

        message = Template(email_info["message"])
        context = Context(
            self.flow.flow_info
            | email_info
            | {"flow": self.flow, "task": self.task_status}
        )

        send_mail(
            subject=email_info["subject"],
            message=message.render(context),
            from_email=email_info["from_email"],
            recipient_list=email_info["recipient_list"],
            fail_silently=False,
        )

        return [], True
