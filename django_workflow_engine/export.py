import networkx as nx

import uuid
import shortuuid
from xml.etree import ElementTree

from django_workflow_engine.utils import lookup_workflow



class WorkflowExporter:
    process_node = None
    start_id = None
    output_diagram = True
    complete = []

    current_x = 0
    current_y = 0

    def __init__(self, workflow):
        self.workflow = workflow

    def print_xml(self, node):
        xml_str = ElementTree.tostring(node, encoding='unicode')
        print(xml_str)

    def get_id(self, prefix):
        return f"{prefix}_{str(shortuuid.uuid())}"

    def create_sequence_flow(self, source_id, target_id):
        """
        <sequenceFlow
            id="SequenceFlow_0h21x7r"
            sourceRef="StartEvent_1y45yut"
            targetRef="Task_1hcentk" />
        """
        seq_flow_id = f"arrow_{source_id}_{target_id}"

        ElementTree.SubElement(
            self.process_node, 'sequenceFlow', {
                "id": seq_flow_id,
                "sourceRef": source_id,
                "targetRef": target_id
            }
        )

        self.create_edge(
            seq_flow_id,
            waypoints=[{
                "x": 100,
                "y": 100,
            }]
        )

    def create_task(self, task_id, name, incoming, outgoing):
        """
        <task id="Task_1hcentk" name="choose recipe">
          <incoming>SequenceFlow_0h21x7r</incoming>
          <outgoing>Flow_1xede4y</outgoing>
        </task>
        """
        node_type = "task"

        if task_id == "complete":
            node_type = "endEvent"

        task = ElementTree.SubElement(
            self.process_node, node_type, {
                "id": task_id,
                "name": name,
            }
        )

        for item in incoming:
            incoming_node = ElementTree.SubElement(
                task, 'incoming'
            )
            incoming_node.text = f"arrow_{item[0]}_{item[1]}"

        for item in outgoing:
            outgoing_node = ElementTree.SubElement(
                task, 'outgoing'
            )
            outgoing_node.text = f"arrow_{item[0]}_{item[1]}"

        """
        <bpmndi:BPMNShape id="Task_1hcentk_di" bpmnElement="Task_1hcentk">
            <omgdc:Bounds x="240" y="160" width="100" height="80" />
        </bpmndi:BPMNShape>
        """
        if task_id == "complete":
            self.create_shape(
                task_id,
                create_label=True,
                x=240,
                y=160,
                w=36,
                h=36,
            )
        else:
            self.create_shape(
                task_id,
                create_label=False,
                x=240,
                y=160,
                w=100,
                h=80,
            )

        return task

    def get_step(self, step_id):
        for step in self.workflow.steps:
            if step.step_id == step_id:
                return step

        raise Exception(f"Step not found for id '{step_id}'")

    def create_edge(self, bpmn_element, waypoints):
        """
        <bpmndi:BPMNEdge id="Flow_1ou53ed_di" bpmnElement="Flow_1ou53ed">
            <omgdi:waypoint x="610" y="260" />
            <omgdi:waypoint x="646" y="260" />
            <omgdi:waypoint x="646" y="200" />
            <omgdi:waypoint x="742" y="200" />
        </bpmndi:BPMNEdge>
        """
        if not self.output_diagram:
            return

        edge_node = ElementTree.SubElement(
            self.canvas_node, "bpmndi:BPMNEdge", {
                "id": f"{bpmn_element}_di",
                "bpmnElement": bpmn_element,
            }
        )

        for waypoint in waypoints:
            ElementTree.SubElement(
                edge_node, "omgdi:waypoint", {
                    "x": str(waypoint["x"]),
                    "y": str(waypoint["y"]),
                }
            )

    def create_shape(self, bpmn_element, create_label=False, x=0, y=0, w=0, h=0):
        """
        <bpmndi:BPMNShape id="StartEvent_1y45yut_di" bpmnElement="StartEvent_1y45yut">
            <omgdc:Bounds x="152" y="182" width="36" height="36" />
            <bpmndi:BPMNLabel>
                <omgdc:Bounds x="134" y="225" width="73" height="14" />
            </bpmndi:BPMNLabel>
        </bpmndi:BPMNShape>
        """
        if not self.output_diagram:
            return

        shape_node = ElementTree.SubElement(
            self.canvas_node, "bpmndi:BPMNShape", {
                "id": f"{bpmn_element}_di",
                "bpmnElement": bpmn_element,
            }
        )

        ElementTree.SubElement(
            shape_node, "omgdc:Bounds", {
                "x": str(x),
                "y": str(y),
                "width": str(w),
                "height": str(h),
            }
        )

        if create_label:
            label = ElementTree.SubElement(
                shape_node, "bpmndi:BPMNLabel",
            )

            ElementTree.SubElement(
                label, "omgdc:Bounds", {
                    "x": str(x),
                    "y": str(y),
                    "width": str(w),
                    "height": str(h),
                }
            )

    def export_bpmn(self):
        ElementTree.register_namespace("trsdf", "http://www.omg.org/spec/BPMN/20100524/MODEL")
        ElementTree.register_namespace("bpmndi", "http://www.omg.org/spec/BPMN/20100524/DI")
        ElementTree.register_namespace("omgdi", "http://www.omg.org/spec/DD/20100524/DI")
        ElementTree.register_namespace("omgdc", "http://www.omg.org/spec/DD/20100524/DC")
        ElementTree.register_namespace("xsi", "http://www.w3.org/2001/XMLSchema-instance")

        root = ElementTree.Element(
            "definitions", {
                "id": str(uuid.uuid4()),
            }
        )

        self.process_node = ElementTree.SubElement(
            root,
            "process", {
                "id": self.workflow.name,
                "isExecutable": "false"
            }
        )

        if self.output_diagram:
            self.diagram_node = ElementTree.SubElement(
                root,
                "bpmndi:BPMNDiagram", {
                    "id": f"{self.workflow.name}_diagram",
                }
            )

            self.canvas_node = ElementTree.SubElement(
                self.diagram_node,
                "bpmndi:BPMNPlane", {
                    "id": f"{self.workflow.name}_diagram_plane",
                    "bpmnElement": self.workflow.name
                }
            )

        """
        <startEvent id="StartEvent_1y45yut" name="hunger noticed">
          <outgoing>SequenceFlow_0h21x7r</outgoing>
        </startEvent>
        """

        self.start_node = ElementTree.SubElement(
            self.process_node, "startEvent", {
                "id": "start",
                "name": "Start",
                "isExecutable": "false",
            }
        )

        self.create_shape("start", 200, 200, 36, 36)

        self.dag = nx.DiGraph()

        for step in self.workflow.steps:
            if step.start:
                self.process_step(step.step_id, "start")

        # Create tasks
        for node in self.dag.nodes:
            # Get incoming, outgoing
            incoming_ids = self.dag.in_edges(node)
            outgoing_ids = self.dag.out_edges(node)

            # TODO name
            self.create_task(
                str(node),
                str(node),
                incoming_ids,
                outgoing_ids,
            )

        for edge in self.dag.edges:
            self.create_sequence_flow(
                edge[0],
                edge[1],
            )

        self.print_xml(root)

        assert False

    def process_step(self, step_id, previous_step_id):
        self.dag.add_edge(previous_step_id, step_id)

        if step_id != "complete":
            step = self.get_step(step_id)

            for target_id in step.targets:
                self.process_step(target_id, step_id)
