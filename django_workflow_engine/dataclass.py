"""django_workflow_engine package framework dataclasses.

Dataclasses that are used to define a custom workflow and its steps.
"""
from dataclasses import dataclass, field
from itertools import dropwhile
from typing import List, Literal, Optional, Type, Union

from django_workflow_engine.tasks import Task


@dataclass
class Step:
    step_id: str
    task_name: str
    targets: Union[List[str], Literal["complete"]]
    start: Optional[bool] = None
    task_info: Optional[dict] = None
    description: Optional[str] = None
    groups: List[str] = field(default_factory=list)
    no_log: Optional[bool] = False

    @property
    def task(self) -> Type[Task]:
        """
        This property returns the uninstantiated Task class for this step.
        """
        return Task.tasks[self.task_name]


@dataclass
class Workflow:
    name: str
    steps: list[Step]

    def get_step(self, step_id) -> Optional[Step]:
        return next((step for step in self.steps if step.step_id == step_id), None)

    @property
    def first_step(self):
        return next(step for step in self.steps if step.start)

    def get_loops(self) -> List[List[str]]:
        loops: List[List[str]] = []
        chains: List[List[str]] = []

        def add_step_to_chains(previous_step_id: str, step_id: str):
            step = self.get_step(step_id=step_id)
            if not step:
                return None

            linked_chains: List[List[str]] = []
            for chain in chains:
                if previous_step_id == chain[-1]:
                    linked_chains.append(chain)

            loop_detected = False

            for linked_chain in linked_chains:
                new_chain = linked_chain.copy()
                if step_id in new_chain:
                    loop_detected = True
                    loop_chain = list(dropwhile(lambda x: x != step_id, new_chain))
                    loops.append(loop_chain)
                    linked_chains.remove(linked_chain)
                else:
                    new_chain.append(step_id)
                    chains.append(new_chain)

            if loop_detected:
                return None

            if step.targets != "complete":
                for target in step.targets:
                    add_step_to_chains(
                        step_id=target,
                        previous_step_id=step_id,
                    )

        chains.append([self.first_step.step_id])

        if self.first_step.targets != "complete":
            for target in self.first_step.targets:
                add_step_to_chains(
                    previous_step_id=self.first_step.step_id, step_id=target
                )

        return loops

    def step_last_in_loop(self, step_id: str) -> bool:
        loops = self.get_loops()

        for loop in loops:
            if step_id == loop[-1]:
                return True

        return False
