import pytest
from django_workflow_engine import COMPLETE, Step, Task, Workflow
from django_workflow_engine.tests.utils import set_up_flow

from django_workflow_engine.export import WorkflowExporter


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
                label="Finance task",
                step_id="test_task_1",
                task_name="Update HR",
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
                label="HR task",
                step_id="test_task_2",
                task_name="task_info_task",
                targets=["test_task_4"],
                task_info={
                    "task_name": "Test task 2",
                },
            ),
            Step(
                pool="Test",
                lane="Finance",
                label="Finance other task",
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
                label="Another HR task",
                step_id="test_task_4",
                task_name="task_info_task",
                targets=[COMPLETE,],
                task_info={
                    "task_name": "Test task 4",
                },
            ),
        ],
    )

    # test_workflow = Workflow(
    #     name="test_workflow",
    #     steps=[
    #         Step(
    #             pool="Test",
    #             lane="HR",
    #             # task_icon="",
    #             step_id="test_task_1",
    #             task_name="task_info_task",
    #             label="HR task",
    #             start=True,
    #             targets=["test_task_2"],
    #             decision_text="Passed credit check?",
    #             description="Blah blah",
    #             task_info={
    #                 "task_name": "Test task 1",
    #             },
    #         ),
    #         Step(
    #             pool="Test",
    #             lane="HR",
    #             # task_icon="",
    #             step_id="test_task_2",
    #             task_name="task_info_task",
    #             label="Finance task",
    #             targets=[COMPLETE,],
    #             task_info={
    #                 "task_name": "Test task 4",
    #             },
    #         ),
    #     ],
    # )

    exporter = WorkflowExporter(test_workflow)
    exporter.export_bpmn()


import bpmn_python.bpmn_diagram_layouter as layouter
import bpmn_python.bpmn_diagram_visualizer as visualizer
import bpmn_python.bpmn_diagram_rep as diagram

output_directory = "./output/test-manual/simple/"
output_file_with_di = "manually-generated-output.xml"
output_file_no_di = "manually-generated-output-no-di.xml"
output_dot_file = "manually-generated-example"
output_png_file = "manually-generated-example"


def test_create_diagram_manually():
    bpmn_graph = diagram.BpmnDiagramGraph()
    bpmn_graph.create_new_diagram_graph(diagram_name="diagram1")
    process_id = bpmn_graph.add_process_to_diagram()
    [start_id, _] = bpmn_graph.add_start_event_to_diagram(
        process_id, start_event_name="start_event",
        start_event_definition="timer"
    )
    [task1_id, _] = bpmn_graph.add_task_to_diagram(process_id, task_name="task1")
    bpmn_graph.add_sequence_flow_to_diagram(process_id, start_id, task1_id, "start_to_one")

    [exclusive_gate_fork_id, _] = bpmn_graph.add_exclusive_gateway_to_diagram(process_id,
                                                                              gateway_name="exclusive_gate_fork")
    [task1_ex_id, _] = bpmn_graph.add_task_to_diagram(process_id, task_name="task1_ex")
    [task2_ex_id, _] = bpmn_graph.add_task_to_diagram(process_id, task_name="task2_ex")
    [exclusive_gate_join_id, _] = bpmn_graph.add_exclusive_gateway_to_diagram(process_id,
                                                                              gateway_name="exclusive_gate_join")

    bpmn_graph.add_sequence_flow_to_diagram(process_id, task1_id, exclusive_gate_fork_id, "one_to_ex_fork")
    bpmn_graph.add_sequence_flow_to_diagram(process_id, exclusive_gate_fork_id, task1_ex_id, "ex_fork_to_ex_one")
    bpmn_graph.add_sequence_flow_to_diagram(process_id, exclusive_gate_fork_id, task2_ex_id, "ex_fork_to_ex_two")
    bpmn_graph.add_sequence_flow_to_diagram(process_id, task1_ex_id, exclusive_gate_join_id, "ex_one_to_ex_join")
    bpmn_graph.add_sequence_flow_to_diagram(process_id, task2_ex_id, exclusive_gate_join_id, "ex_two_to_ex_join")

    [task2_id, _] = bpmn_graph.add_task_to_diagram(process_id, task_name="task2")
    [end_id, _] = bpmn_graph.add_end_event_to_diagram(process_id, end_event_name="end_event",
                                                      end_event_definition="message")
    bpmn_graph.add_sequence_flow_to_diagram(process_id, exclusive_gate_join_id, task2_id, "ex_join_to_two")
    bpmn_graph.add_sequence_flow_to_diagram(process_id, task2_id, end_id, "two_to_end")

    layouter.generate_layout(bpmn_graph)

    bpmn_graph.export_xml_file(output_directory, output_file_with_di)
    bpmn_graph.export_xml_file_no_di(output_directory, output_file_no_di)
    # Uncomment line below to get a simple view of created diagram
    # visualizer.visualize_diagram(bpmn_graph)
    #visualizer.bpmn_diagram_to_dot_file(bpmn_graph, output_directory + output_dot_file)
    visualizer.bpmn_diagram_to_png(bpmn_graph, output_directory + output_png_file)
