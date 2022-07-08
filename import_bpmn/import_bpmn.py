import os

import bpmn_python.bpmn_diagram_rep as diagram
from django_workflow_engine import Step, Workflow


def output_step(step:Step):
    start_value = ""
    if step.start:
        start_value = "start=True,"
    targets = ""
    if step.targets:
        targets = "targets=["
        for target in step.targets:
            targets = f'{targets}"{target}", '
        targets = f"{targets}],, "
    output = f'''Step(
        label="{step.label}",
        step_id="{step.step_id}",
        task_name="{step.label}",
        {start_value}
        {targets}
        targets=[
            "check_uksbs_line_manager",
        ],
    ),'''
    return output_step


def output_workflow(workflow:Workflow, file):
    file.write(f'''    
    test_workflow = Workflow(
        name="{workflow.name}",
        steps=[
    ''')
    for step in workflow.steps:
        file.write(output_step(step))
    file.write('''
            ],
    )
    ''')


def translate_node_to_step(node):
    step = Step()
    step.step_id = node['id']
    step.start = node['type'] == 'startEvent'
    step.label = node['node_name']
    step.targets = node["outgoing"]
    return step

def make_name_from_label(label):
    return label.replace(" ","_").lower()

def import_BPMN(xml_file_path, work_flow_name, output_file_path):
    bpmn_graph = diagram.BpmnDiagramGraph()
    bpmn_graph.load_diagram_from_xml_file(xml_file_path)
    step_list = []
    step_translation = {}
    for node in bpmn_graph.diagram_graph._node:
        step_list.append(translate_node_to_step(node.value))
        step_translation[node.key] = make_name_from_label(node.value['node_name'])

#     convert the id in the workflow nodes to human names
    for step in step_list:
        target_list = []
        step.step_id = step_translation[step.step_id]
        if step.targets:
            for target in step.targets:
                target_list.append(step_translation[target])
        step.targets = target_list

    workflow = Workflow()
    workflow.name = work_flow_name
    workflow.steps = step_list
    output_file = open(output_file_path, "w")
    output_workflow(workflow, output_file)
    output_file.close()

