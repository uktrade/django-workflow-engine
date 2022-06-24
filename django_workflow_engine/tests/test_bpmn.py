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

    test_workflow = Workflow(
        name="test_workflow",
        steps=[
            Step(
                pool="Test",
                lane="HR",
                # task_icon="",
                step_id="test_task_1",
                task_name="task_info_task",
                label="HR task",
                start=True,
                targets=["test_task_2"],
                decision_text="Passed credit check?",
                description="Blah blah",
                task_info={
                    "task_name": "Test task 1",
                },
            ),
            Step(
                pool="Test",
                lane="HR",
                # task_icon="",
                step_id="test_task_2",
                task_name="task_info_task",
                label="Finance task",
                targets=[COMPLETE,],
                task_info={
                    "task_name": "Test task 4",
                },
            ),
        ],
    )

    test_workflow = Workflow(
        name="leaving",
        steps=[
            # Leaver
            Step(
                label="Setup leaving",
                step_id="setup_leaving",
                task_name="basic_task",
                start=True,
                targets=[
                    "check_uksbs_line_manager",
                ],
            ),
            Step(
                label="Check UKSBS line manager",
                step_id="check_uksbs_line_manager",
                task_name="check_uksbs_line_manager",
                targets=[
                    #"send_line_manager_correction_reminder",
                    "notify_line_manager",
                ],
            ),
            Step(
                label="Send line manager correction reminder",
                step_id="send_line_manager_correction_reminder",
                task_name="reminder_email",
                targets=[
                    "check_uksbs_line_manager",
                ],
                break_flow=True,
                task_info={
                    "email_id": "",
                },
            ),
            # Line manager
            Step(
                label="Notify line manager",
                step_id="notify_line_manager",
                task_name="notification_email",
                targets=[
                    "has_line_manager_completed",
                ],
                task_info={
                    "email_id": "",
                },
            ),
            Step(
                label="Has line manager completed?",
                step_id="has_line_manager_completed",
                task_name="has_line_manager_completed",
                targets=[
                    #"send_line_manager_reminder",
                    "thank_line_manager",
                ],
            ),
            Step(
                label="Send line manager reminder",
                step_id="send_line_manager_reminder",
                task_name="reminder_email",
                targets=[
                    "has_line_manager_completed",
                ],
                break_flow=True,
                task_info={
                    "email_id": "",
                },
            ),
            Step(
                label="Thank line manager",
                step_id="thank_line_manager",
                task_name="notification_email",
                targets=[
                    "send_uksbs_leaver_details",
                ],
                task_info={
                    "email_id": "",
                },
            ),
            # UK SBS
            Step(
                label="Send UKSBS leaver details",
                step_id="send_uksbs_leaver_details",
                task_name="send_uksbs_leaver_details",
                targets=[
                    "setup_scheduled_tasks",
                ],
            ),
            # Split flow
            Step(
                label="Setup scheduled tasks",
                step_id="setup_scheduled_tasks",
                task_name="basic_task",
                targets=[
                    "send_service_now_leaver_details",
                    "send_lsd_team_leaver_details",
                    "notify_csu4_of_leaving",
                    "notify_csu4_of_leaving",
                    "notify_ocs_of_leaving",
                    "notify_ocs_of_oab_locker",
                    "send_security_notification",
                    "is_it_leaving_date_plus_x",
                ],
            ),
            # Service Now
            Step(
                label="Send Service Now leaver details",
                step_id="send_service_now_leaver_details",
                task_name="send_service_now_leaver_details",
                targets=[
                    "are_all_tasks_complete",
                ],
            ),
            # LSD
            Step(
                label="Send LSD team leaver details",
                step_id="send_lsd_team_leaver_details",
                task_name="send_lsd_team_leaver_details",
                targets=[
                    "are_all_tasks_complete",
                ],
            ),
            # CSU4
            Step(
                label="Notify CSU4 of leaving",
                step_id="notify_csu4_of_leaving",
                task_name="notification_email",
                targets=[
                    "are_all_tasks_complete",
                ],
                task_info={
                    "email_id": "",
                },
            ),
            # OCS
            Step(
                label="Notify OCS of leaving",
                step_id="notify_ocs_of_leaving",
                task_name="notification_email",
                targets=[
                    "are_all_tasks_complete",
                ],
                task_info={
                    "email_id": "",
                },
            ),
            # OCS OAB Lockers
            Step(
                label="Notify OCS of OAB locker",
                step_id="notify_ocs_of_oab_locker",
                task_name="notification_email",
                targets=[
                    "are_all_tasks_complete",
                ],
                task_info={
                    "email_id": "",
                },
            ),
            # SECURITY
            Step(
                label="Send security notification",
                step_id="send_security_notification",
                task_name="notification_email",
                targets=[
                    "have_security_carried_out_leaving_tasks",
                ],
                task_info={
                    "email_id": "",
                },
                break_flow=True,
            ),
            Step(
                label="Have security carried out leaving tasks?",
                condition=True,
                step_id="have_security_carried_out_leaving_tasks",
                task_name="have_security_carried_out_leaving_tasks",
                targets=[
                    #"send_security_reminder",
                    "are_all_tasks_complete",
                ],
            ),
            Step(
                label="Send security reminder",
                step_id="send_security_reminder",
                task_name="reminder_email",
                targets=[
                    "have_security_carried_out_leaving_tasks",
                ],
                task_info={
                    "email_id": "",
                },
                break_flow=True,
            ),
            # SRE
            Step(
                label="Is it leaving date plus x?",
                step_id="is_it_leaving_date_plus_x",
                task_name="is_it_leaving_date_plus_x",
                targets=[
                    "send_sre_slack_message",
                ],
                break_flow=True,
            ),
            Step(
                label="Send SRE Slack message",
                step_id="send_sre_slack_message",
                task_name="send_sre_slack_message",
                targets=[
                    "have_sre_carried_out_leaving_tasks",
                ],
            ),
            Step(
                label="Have SRE carried out leaving tasks?",
                step_id="have_sre_carried_out_leaving_tasks",
                task_name="have_sre_carried_out_leaving_tasks",
                targets=[
                    #"send_sre_reminder",
                    "are_all_tasks_complete",
                ],
            ),
            Step(
                label="Send SRE reminder",
                step_id="send_sre_reminder",
                task_name="reminder_email",
                targets=[
                    "have_sre_carried_out_leaving_tasks",
                ],
                task_info={
                    "email_id": "",
                },
                break_flow=True,
            ),
            # End
            Step(
                label="Are all tasks completed?",
                step_id="are_all_tasks_complete",
                task_name="leaver_complete",
                targets=[COMPLETE],
            ),
        ],
    )

    exporter = WorkflowExporter(test_workflow)
    exporter.export_bpmn()
