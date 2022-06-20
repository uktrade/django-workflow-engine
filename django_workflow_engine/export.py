import uuid
import shortuuid
from xml.etree import ElementTree

from django_workflow_engine.utils import lookup_workflow


#ALPHABET = string.ascii_lowercase + string.digits


def print_xml(node):
    xml_str = ElementTree.tostring(node, encoding='unicode')
    print(xml_str, flush=True)


def get_id(prefix):
    return f"{prefix}_{shortuuid.ShortUUID()}"


def create_arrow(parent_element, source, target):
    """
    <sequenceFlow
        id="SequenceFlow_0h21x7r"
        sourceRef="StartEvent_1y45yut"
        targetRef="Task_1hcentk" />
    """

    print("b4 arrow", flush=True)
    print(source, flush=True)
    print(target, flush=True)
    print("/b4 arrow")

    arrow = ElementTree.SubElement(
        parent_element, 'sequenceFlow', {
            "id": get_id("Flow"),
            "sourceRef": source,
            "targetRef": target
        }
    )

    print("arrow")
    print_xml(arrow, flush=True)
    print("/arrow")


def create_task(parent_element, id, name, from_items, to_items):
    """
    <task id="Task_1hcentk" name="choose recipe">
      <incoming>SequenceFlow_0h21x7r</incoming>
      <outgoing>Flow_1xede4y</outgoing>
    </task>
    """
    task = ElementTree.SubElement(
        parent_element, 'task', {
            "id": id,
            "name": name,
        }
    )

    print_xml(task)

    for incoming in from_items:
        incoming = ElementTree.SubElement(
            task, 'incoming',
        )
        incoming.text = incoming

        print_xml(incoming)

    for outgoing in to_items:
        outgoing = ElementTree.SubElement(
            task, 'outgoing'
        )
        outgoing.text = outgoing

        print_xml(outgoing)


def generate_bpmn_xml(workflow):
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

    process = ElementTree.SubElement(
        root,
        "process", {
            "id": workflow.name,
            "isExecutable": "false"
        }
    )

    """
    <startEvent id="StartEvent_1y45yut" name="hunger noticed">
      <outgoing>SequenceFlow_0h21x7r</outgoing>
    </startEvent>
    """

    start = ElementTree.SubElement(
        process, "startEvent", {
            "id": get_id("StartEvent"),
            "name": "Start",
            "isExecutable": False
        }
    )

    arrows = []
    linked = ["start", ]

    for step in workflow.steps:
        # Create task

        print(step.step_id)
        print(step.task_name)

        task = create_task(
            process,
            step.step_id,
            step.task_name,
            linked,
            step.targets,
        )

        for link in linked:
            print(link)
            arrows.append({
                "from": step.step_id,
                "to": link
            })

        linked = step.targets

    print("Hier...")
    print_xml(root)
    print("Hierd...")
    assert False
