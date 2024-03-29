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

combine_workflow = Workflow(
    name="combine_workflow",
    steps=[
        Step(
            step_id="canterbury",
            task_name=LogMessageTask.task_name,
            start=True,
            targets=["rochester"],
            task_info={
                "message": "you're in Canterbury"
            }
        ),
        Step(
            step_id="rochester",
            task_name=LogMessageTask.task_name,
            start=True,
            targets=["london"],
            task_info={
                "message": "you're in Rochester"
            }
        ),
        Step(
            step_id="colchester",
            task_name=LogMessageTask.task_name,
            start=True,
            targets=["chelmsford"],
            task_info={
                "message": "you're in Colchester"
            }
        ),
        Step(
            step_id="chelmsford",
            task_name=LogMessageTask.task_name,
            start=True,
            targets=["london"],
            task_info={
                "message": "you're in Chelmsford"
            }
        ),
        Step(
            step_id="london",
            task_name=LogMessageTask.task_name,
            start=True,
            targets=COMPLETE,
            task_info={
                "message": "you're finished in London"
            }
        ),
    ],
)

infinite_loop_workflow = Workflow(
    name="infinite_loop_workflow",
    steps=[
        Step(
            step_id="wake_up",
            task_name=LogMessageTask.task_name,
            start=True,
            targets=["eat"],
            task_info={
                "message": "you're awake"
            }
        ),
        Step(
            step_id="eat",
            task_name=LogMessageTask.task_name,
            start=True,
            targets=["party"],
            task_info={
                "message": "you're eating"
            }
        ),
        Step(
            step_id="party",
            task_name=LogMessageTask.task_name,
            start=True,
            targets=["party"],
            task_info={
                "message": "you're partying"
            }
        ),
        Step(
            step_id="sleep",
            task_name=LogMessageTask.task_name,
            start=True,
            targets=["wake_up"],
            task_info={
                "message": "you're sleep"
            }
        ),
    ],
)
