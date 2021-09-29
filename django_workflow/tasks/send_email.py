from django.core.mail import send_mail
from django.template import Context, Template

from .task import Task


class SendEmail(Task, input="send_email"):
    auto = True

    def execute(self, task_info):
        email_info = self.task_record.task_info | task_info

        message = Template(email_info["message"])
        context = Context(
            self.flow.flow_info
            | email_info
            | {"flow": self.flow, "task": self.task_record}
        )

        successfully_sent = send_mail(
            subject=email_info["subject"],
            message=message.render(context),
            from_email=email_info["from_email"],
            recipient_list=email_info["recipient_list"],
            fail_silently=False,
        )

        return None, {"successfully_sent": successfully_sent}
