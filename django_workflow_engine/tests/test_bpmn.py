import pytest
from django_workflow_engine import COMPLETE, Step, Task, Workflow
from django_workflow_engine.tests.utils import set_up_flow

from django_workflow_engine.export import generate_bpmn_xml


class TaskInfoTask(Task):
    task_name = "task_info_task"
    auto = True

    def execute(self, task_info):
        print("Task name: ", task_info["task_name"])
        return None, {}, True


@pytest.mark.django_db
def test_bpmn_xml_export(settings):
    test_workflow = Workflow(
        name="test_workflow",
        steps=[
            Step(
                pool="Test",
                lane="HR",
                # task_icon="",
                step_id="test_task_1",
                task_name="task_info_task",
                start=True,
                targets=["test_task_2", "test_task_3"],
                decision_text="Passed credit check?",
                description="Blah blah",
                task_info={
                    "task_name": "Test task 1",
                },
            ),
            Step(
                pool="Test",
                lane="Finance",
                # task_icon="",
                step_id="test_task_2",
                task_name="task_info_task",
                targets=["test_task_3"],
                task_info={
                    "task_name": "Test task 2",
                },
            ),
            Step(
                pool="Test",
                lane="Finance",
                # task_icon="",
                step_id="test_task_3",
                task_name="task_info_task",
                targets=["test_task_4"],
                task_info={
                    "task_name": "Test task 3",
                },
            ),
            Step(
                pool="Test",
                lane="HR",
                # task_icon="",
                step_id="test_task_4",
                task_name="task_info_task",
                targets=COMPLETE,
                task_info={
                    "task_name": "Test task 4",
                },
            ),
        ],
    )

    generate_bpmn_xml(test_workflow)


    
