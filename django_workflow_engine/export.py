import networkx as nx

import bpmn_python.bpmn_diagram_layouter as layouter
import bpmn_python.bpmn_diagram_rep as diagram


class WorkflowExporter:
    process_node = None
    start_id = None
    output_diagram = True
    complete = []

    completed_edges = []

    def __init__(self, workflow):
        self.workflow = workflow
        self.create_dag()

    def get_step(self, step_id):
        for step in self.workflow.steps:
            if step.step_id == step_id:
                return step

        raise Exception(f"Step not found for id '{step_id}'")

    def create_dag(self):
        self.dag = nx.DiGraph()

        for step in self.workflow.steps:
            if step.start:
                self.process_step(step.step_id, "start")

    def process_step(self, step_id, previous_step_id):
        self.dag.add_edge(previous_step_id, step_id)

        if step_id != "complete":
            step = self.get_step(step_id)

            for target_id in step.targets:
                if f"{step_id}_{target_id}" not in self.completed_edges:
                    self.completed_edges.append(f"{step_id}_{target_id}")
                    self.process_step(target_id, step_id)

    def export_bpmn(self):
        self.bpmn_graph = diagram.BpmnDiagramGraph()
        self.bpmn_graph.create_new_diagram_graph(diagram_name=self.workflow.name)
        self.process_id = self.bpmn_graph.add_process_to_diagram()

        id_lookup = {}

        for node in self.dag.nodes:
            if str(node) == "start":
                [object_id, _] = self.bpmn_graph.add_start_event_to_diagram(
                    self.process_id, start_event_name="start_event",
                )
            elif str(node) == "complete":
                [object_id, _] = self.bpmn_graph.add_end_event_to_diagram(
                    self.process_id,
                    end_event_name="end_event",
                )
            else:
                step = self.get_step(node)
                if step.condition:
                    [object_id, _] = self.bpmn_graph.add_exclusive_gateway_to_diagram(
                        self.process_id,
                        gateway_name=step.label
                    )
                else:
                    [object_id, _] = self.bpmn_graph.add_task_to_diagram(
                        self.process_id,
                        task_name=step.label,
                    )
            id_lookup[str(node)] = object_id

        for edge in self.dag.edges:
            from_id = id_lookup[str(edge[0])]
            to_id = id_lookup[str(edge[1])]

            self.bpmn_graph.add_sequence_flow_to_diagram(
                self.process_id,
                from_id,
                to_id,
            )

        layouter.generate_layout(self.bpmn_graph)

        output_directory = "./output/test-manual/simple/"
        output_file_with_di = "manually-generated-output.xml"

        self.bpmn_graph.export_xml_file(output_directory, output_file_with_di)

        assert False
