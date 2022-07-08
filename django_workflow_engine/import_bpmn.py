from django_workflow_engine import Step, Workflow
import bpmn_python.bpmn_diagram_rep as diagram


def output_step(step:Step):
    # generate the Python code for a step inside the workflow
    start_value = ""
    if step.start:
        start_value = """
        start=True,"""
    if step.targets:
        targets = "targets=["
        for target in step.targets:
            targets = f'{targets}"{target}", '
        targets = f"{targets}], "
    else:
        targets = "targets=[COMPLETE, ]"

    condition = ""
    if step.condition:
        condition = """
        condition=True,"""

    output = f'''Step(
        label="{step.label}",
        step_id="{step.step_id}",
        task_name="{step.step_id}_task",{start_value}{condition}
        {targets}
    ),
    '''
    return output


def output_workflow(workflow:Workflow, file):
    # Generate the Python code for the workflow
    # Add the relevant import
    file.write("""from django_workflow_engine import COMPLETE, Step, Workflow
    
    """)
    # Generate the workflow
    file.write(f'''    
bpmn_imported_workflow = Workflow(
        name="{workflow.name}",
        steps=[
    ''')
    for step in workflow.steps:
        step_output = output_step(step)
        file.write(step_output)
    file.write('''
            ],
    )
    ''')


def translate_node_to_step(node):
    # TODO add the format of the node
    step = Step(node['id'], node['node_name'], node['node_name'], node["outgoing"])
    step.start = node['type'] == 'startEvent'
    if node['type'] == 'exclusiveGateway':
        step.condition = True
    return step


def make_name_from_label(label):
    return label.replace(" ","_").lower()


def import_BPMN(xml_file_path,  output_file_path):
    # TODO add error handling
    bpmn_graph = diagram.BpmnDiagramGraph()
    bpmn_graph.load_diagram_from_xml_file(xml_file_path)
    work_flow_name = bpmn_graph.diagram_attributes['name']
    step_list = []
    step_translation = {}

    for node in bpmn_graph.get_nodes():
        workflow_node = translate_node_to_step(node[1])
        step_list.append(workflow_node)
        name_from_label = make_name_from_label(node[1]['node_name'])
        step_translation[node[0]] = name_from_label
        for incoming_node in node[1]['incoming']:
            step_translation[incoming_node] = name_from_label

    #  convert the id in the workflow nodes to human names
    for step in step_list:
        target_list = []
        step.step_id = step_translation[step.step_id]
        if step.targets:
            for target in step.targets:
                target_list.append(step_translation[target])
        step.targets = target_list

    workflow = Workflow( work_flow_name, step_list)
    output_file = open(output_file_path, "w")
    output_workflow(workflow, output_file)
    output_file.close()
