from django_workflow_engine import Step, Workflow


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
