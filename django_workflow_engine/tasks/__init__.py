"""django workflow tasks package.

Surface task things into the framework package.
"""
from .email_form import EmailFormTask
from .send_email import SendEmail
from .task import Task, TaskError
