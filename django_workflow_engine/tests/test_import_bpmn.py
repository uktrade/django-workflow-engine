import pytest
from django_workflow_engine.import_bpmn import import_BPMN


@pytest.mark.django_db
def test_bpmn_xml_import(settings):
    python_path = "./output/test-manual/simple/broken.py"
    bpmn_path = "./output/test-manual/simple/manually-generated-output_1.xml"
    # bpmn_path = "./output/test-manual/simple/bpmn_editor_simple_example.xml"

    import_BPMN(bpmn_path, python_path)

