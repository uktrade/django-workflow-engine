"""Django workflow Task.

A task is an instance of a django_workflow_engine.dataclasses.Step
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Dict, List, Literal, Optional, Tuple, Type, Union

if TYPE_CHECKING:
    from django_workflow_engine.models import Flow, TaskStatus


class TaskError(Exception):
    """Base exception for tasks."""

    def __init__(self, message, context=None):
        if context is None:
            context = {}

        self.message = message
        self.context = context


class Task(ABC):
    """Base class for all tasks.

    Attributes:
        tasks: Internal mapping of task name to task class.
        auto: Whether the task is automatic or manual. Defaults to False (manual).
        abstract: Whether the task is an abstract task. Defaults to False.
        task_name: The name which will be used to map to the task class in `tasks`.
    """

    tasks: dict[str, Type["Task"]] = {}

    auto: bool = False
    abstract: bool = False
    task_name: Optional[str] = None

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)

        if cls.abstract and cls.task_name:
            raise TaskError("Abstract tasks should not have a task_name")

        if not cls.abstract and not cls.task_name:
            raise TaskError("Tasks should have a task_name")

        if not cls.abstract and cls.task_name:
            cls.tasks[cls.task_name] = cls

    def __init__(self, user, task_status: "TaskStatus", flow: "Flow") -> None:
        self.user = user
        self.task_status: "TaskStatus" = task_status
        self.flow: "Flow" = flow

    def setup(self, task_info: Dict) -> None:
        pass

    @abstractmethod
    def execute(
        self,
        task_info: Dict,
    ) -> Tuple[Union[List[str], Literal["complete"]], bool]:
        raise NotImplementedError

    def log(self, message: str) -> None:
        self.task_status.log.create(message=message)
