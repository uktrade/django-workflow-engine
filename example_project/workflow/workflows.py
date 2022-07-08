from django_workflow_engine import COMPLETE, Step, Workflow
from django_workflow_engine.tests.tasks import BasicTask
from example_project.workflow.tasks import LogMessageTask

simple_workflow = Workflow(
    name="simple_workflow",
    steps=[
        Step(
            step_id="log_hello_world",
            task_name="log_message",
            targets=["log_name"],
            start=True,
            task_info={
                "message": "Hello World!",
            },
        ),
        Step(
            step_id="log_name",
            task_name="log_message",
            targets="complete",
            task_info={
                "message": "Sam",
            },
        ),
    ],
)

split_and_join_workflow = Workflow(
    name="split_and_join_workflow",
    steps=[
        Step(
            step_id="open_eyes",
            task_name=LogMessageTask.task_name,
            start=True,
            targets=["get_out_of_bed"],
            task_info={
                "message": "good morning"
            }
        ),
        Step(
            step_id="get_out_of_bed",
            task_name=LogMessageTask.task_name,
            start=True,
            targets=["brush_teeth"],
            task_info={
                "message": "Get out of bed"
            }
        ),
        Step(
            step_id="brush_teeth",
            task_name=LogMessageTask.task_name,
            start=True,
            targets=["stay_at_home", "go_to_work"],
            task_info={
                "message": "Brushing your teeth"
            }
        ),
        Step(
            step_id="stay_at_home",
            task_name=BasicTask.task_name,
            targets=["watch_tv"],
        ),
        Step(
            step_id="go_to_work",
            task_name=BasicTask.task_name,
            targets=["work_hard"],
        ),
        Step(
            step_id="work_hard",
            task_name=BasicTask.task_name,
            task_info={
                "message": "Working hard from the office"
            },
            targets=["drive_home"]
        ),
        Step(
            step_id="drive_home",
            task_name=BasicTask.task_name,
            task_info={
                "message": "Driving home"
            },
            targets=["watch_tv"]
        ),
        Step(
            step_id="watch_tv",
            task_name=BasicTask.task_name,
            targets=COMPLETE,
        ),
    ],
)
