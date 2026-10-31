"""Owner final-write profiles, using real helper outputs offline."""

import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest

from test_notion_checks import CHECKS, SCRIPTS
from test_workflow_checks import task
from test_reply_transport import ADAPTER, fixture

RUN, TASK, ACTION, HUB, LOGS = [c * 32 for c in "abcde"]
PROFILES = json.loads((SCRIPTS.parent / "references/owner-completion-profiles.json").read_text())


def page(identity, body):
    return {"id": identity, "metadata": {"type": "page"}, "text": '<content>\n' + body + '\n</content>'}


def completion_for(owner, step=None):
    steps = {"eightdegrees-communication-context-process": "CompleteCommunicationData",
             "eightdegrees-sales-reply": "ReviewReplyDraft", "eightdegrees-sms-follow-up": "PrepareSmsFollowUp"}
    step = step or steps.get(owner)
    required, results = {}, []
    registry = {"owner_skill": owner, "policy": "owner-workflow", "invocation_id": "run-1",
                "publication_version": "publication-v1", "run_page_ids": [RUN],
                "publication_page_ids": [HUB], "operation_log_source_ids": [LOGS],
                "task_versions": {TASK: "test-v1"} if step else {}, "action_bindings": {ACTION: TASK} if step else {},
                "task_page_ids": [TASK] if step else [], "action_page_ids": [ACTION] if step else []}
    if owner == "eightdegrees-automation-control":
        registry["policy"] = "scheduling-only"

    def add(name, kind, identity, result):
        required[name] = {"kind": kind, "entity_id": identity}
        results.append({"name": name, "invocation_id": "run-1", "publication_version": "publication-v1",
                        "exit_code": 0, "result": result})
    for identity in [RUN, HUB] + ([TASK] if step else []):
        add(identity, "page-links", identity, CHECKS.page_links({"page": page(identity, "Current business result retained.")}))
    if step:
        item = task(step, "Manual"); item["PageId"] = TASK
        # Use the same actual route helper entry point as runtime, not a made-up route success.
        import workflow_checks
        route = workflow_checks.check_resume(item, "owner-workflow", True)
        add("route", "route", TASK, route)
        display = CHECKS.task_display({"page": page(ACTION, "## Current status\n\nVersion: test-v1.\n\n## Processing result\n\nReview pending."), "task": item})
        add("action", "task-display", ACTION, display)
    registry["required_checks"] = copy.deepcopy(required)
    gate = {"invocation_id": "run-1", "publication_version": "publication-v1", "required_checks": required, "checks": results}
    return {"registry": registry, "completion": gate, "call": {"tool": "mcp__codex_apps__notion_notion_update_page",
            "args": {"page_id": RUN, "command": "update_properties", "properties": {"Status": "Completed"}}}}


class OwnerCompletionTests(unittest.TestCase):
    def test_notification_completion_uses_standing_authority_and_actual_body_digest_without_a_decision(self):
        from test_sms_authority import inputs, saved
        import sms_authority
        from test_scheduled_outcomes import saved_outcome, outcome
        import outcome_checks
        data = completion_for('eightdegrees-sms-follow-up', 'SendNotificationSms')
        self.assertEqual(CHECKS.owner_write(data)['status'], 'Deferred')
        source = inputs(); source['payload']['task_id'] = TASK; source['payload']['content_version'] = 'test-v1'
        source['saved_task'] = saved(source) | {'id': TASK}
        authority = sms_authority.verify(source)
        event = outcome('sms','SentToNetwork'); event['provider']['payload_sha256'] = authority['body_sha256']
        for name, kind, result in [('authority','sms-authority',authority),
                                   ('outcome','outcome',outcome_checks.verify_projection(saved_outcome(event)))]:
            spec = {'kind':kind,'entity_id':TASK}
            data['registry']['required_checks'][name] = spec
            data['completion']['required_checks'][name] = spec
            data['completion']['checks'].append({'name':name,'invocation_id':'run-1',
                'publication_version':'publication-v1','exit_code':0,'result':result})
        self.assertEqual(CHECKS.owner_write(data)['status'], 'WithinOwnerScope')
        for digest in (None, 'a'*64):
            bad = copy.deepcopy(data)
            next(x for x in bad['completion']['checks'] if x['name']=='outcome')['result']['expected']['payload_sha256'] = digest
            self.assertEqual(CHECKS.owner_write(bad)['status'], 'Deferred')

    def test_manual_review_queue_completion_requires_current_accepted_submission_without_continue(self):
        import workflow_checks
        data = completion_for('eightdegrees-communication-context-process', 'ReviewCommunication')
        data['registry']['policy'] = 'one-cycle-approved-work'
        item = task('ReviewCommunication','Manual'); item.update(PageId=TASK, ActionPageURL='https://app.notion.com/p/'+ACTION, OperatorId='operator-1')
        route = next(x for x in data['completion']['checks'] if x['name']=='route')
        route['result'] = workflow_checks.check_resume(item,'one-cycle-approved-work')
        self.assertEqual(CHECKS.owner_write(data)['status'],'Deferred')
        item['AcceptedSubmission'] = {'read_verified':True,'task_id':TASK,'action_page_id':ACTION,
            'operator_id':'operator-1','content_version':'test-v1','input_sha256':'f'*64}
        route['result'] = workflow_checks.check_resume(item,'one-cycle-approved-work')
        self.assertEqual(CHECKS.owner_write(data)['status'],'WithinOwnerScope')

    def test_public_approved_cycle_completion_keeps_automatic_route_policy_binding(self):
        import workflow_checks
        data = completion_for('eightdegrees-sales-reply')
        data['registry']['policy'] = 'one-cycle-approved-work'
        self.assertEqual(CHECKS.owner_write(data)['status'], 'Deferred')
        item = task('ReviewReplyDraft', 'Automatic'); item['PageId'] = TASK
        route = next(x for x in data['completion']['checks'] if x['name'] == 'route')
        route['result'] = workflow_checks.check_resume(item, 'one-cycle-approved-work')
        self.assertEqual(CHECKS.owner_write(data)['status'], 'WithinOwnerScope')
        item['Mode'] = 'Manual'
        route['result'] = workflow_checks.check_resume(item, 'one-cycle-approved-work', True)
        self.assertEqual(CHECKS.owner_write(data)['status'], 'Deferred')

    def test_handoff_recovery_cannot_complete_without_persisted_original_task_evidence(self):
        data = completion_for('eightdegrees-sales-reply', 'RecordMaterialHandoff')
        self.assertEqual(CHECKS.owner_write(data)['status'], 'Deferred')
        from test_material_handoff import inputs as handoff_input, saved
        import material_handoff
        handoff = handoff_input(); handoff['email_task_id'] = TASK
        result = material_handoff.verify({'input': handoff,
            'saved_email_task': saved(handoff, 'email') | {'id': TASK}, 'saved_cycle': saved(handoff)})
        spec = {'kind': 'material-handoff', 'entity_id': TASK}
        data['registry']['required_checks']['handoff'] = spec
        data['completion']['required_checks']['handoff'] = spec
        data['completion']['checks'].append({'name': 'handoff', 'invocation_id': 'run-1',
            'publication_version': 'publication-v1', 'exit_code': 0, 'result': result})
        self.assertEqual(CHECKS.owner_write(data)['status'], 'WithinOwnerScope')

    def test_automation_owner_requires_schedule_only_policy_and_cannot_impersonate_business_owner(self):
        data = completion_for("eightdegrees-automation-control")
        self.assertEqual(CHECKS.owner_write(data)["status"], "WithinOwnerScope")
        data["registry"]["policy"] = "owner-workflow"
        self.assertEqual(CHECKS.owner_write(data)["status"], "Deferred")
        data = completion_for("eightdegrees-email-scanning"); data["registry"]["policy"] = "scheduling-only"
        self.assertEqual(CHECKS.owner_write(data)["status"], "Deferred")

    def test_scheduled_completion_needs_current_guard_and_matching_automatic_route(self):
        from test_schedule_checks import SCHEDULE, scheduled_guard
        import workflow_checks
        data = completion_for('eightdegrees-sales-reply')
        data['registry']['policy'] = 'scheduled-approved-work'
        self.assertEqual(CHECKS.owner_write(data)['status'], 'Deferred')
        guard = SCHEDULE.guard(scheduled_guard())
        data['registry'].update(schedule_guard=guard, operator_id=guard['operator_id'])
        item = task('ReviewReplyDraft', 'Automatic'); item.update(PageId=TASK, OperatorId=guard['operator_id'])
        route = next(x for x in data['completion']['checks'] if x['name'] == 'route')
        route['result'] = workflow_checks.check_resume(item, 'scheduled-approved-work', schedule_guard=guard)
        self.assertEqual(CHECKS.owner_write(data)['status'], 'WithinOwnerScope')
        data['registry']['schedule_guard'] = {**guard, 'operator_id': 'different'}
        self.assertEqual(CHECKS.owner_write(data)['status'], 'Deferred')

    def test_registration_proof_cannot_replace_execution_route_at_completion(self):
        data = completion_for("eightdegrees-communication-context-process")
        route = next(r for r in data["completion"]["checks"] if r["name"] == "route")
        route["result"]["status"] = "ValidResumeRoute"
        route["result"]["phase"] = "register"
        self.assertEqual(CHECKS.owner_write(data)["status"], "Deferred")

    def test_each_owner_refuses_completion_without_its_contract(self):
        for owner in PROFILES:
            with self.subTest(owner=owner):
                data = completion_for(owner); del data["completion"]
                self.assertEqual(CHECKS.owner_write(data)["status"], "Deferred")

    def test_each_owner_accepts_current_complete_profile(self):
        for owner in PROFILES:
            with self.subTest(owner=owner):
                self.assertEqual(CHECKS.owner_write(completion_for(owner))["status"], "WithinOwnerScope")

    def test_init_and_scan_cannot_skip_frozen_required_page(self):
        for owner in ("eightdegrees-initialization", "eightdegrees-email-scanning"):
            data = completion_for(owner); data["completion"]["checks"].pop()
            self.assertEqual(CHECKS.owner_write(data)["status"], "Deferred")

    def test_wrong_owner_policy_outside_target_and_report_policy_are_deferred(self):
        for change in ("policy", "target", "report"):
            data = completion_for("eightdegrees-communication-context-process")
            if change == "policy": data["registry"]["policy"] = "setup-only"
            elif change == "report": data["registry"]["policy"] = "report-only"
            else: data["call"]["args"]["page_id"] = "f" * 32
            self.assertEqual(CHECKS.owner_write(data)["status"], "Deferred")

    def test_required_contract_cannot_be_shrunk_after_checks(self):
        data = completion_for("eightdegrees-communication-context-process")
        del data["completion"]["required_checks"]["route"]
        self.assertEqual(CHECKS.owner_write(data)["status"], "Deferred")

    def test_communication_completion_does_not_pass_with_just_display_and_links(self):
        data = completion_for("eightdegrees-communication-context-process")
        del data["registry"]["required_checks"]["route"]
        del data["completion"]["required_checks"]["route"]
        data["completion"]["checks"] = [r for r in data["completion"]["checks"] if r["name"] != "route"]
        self.assertEqual(CHECKS.owner_write(data)["status"], "Deferred")

    def test_original_bad_waiting_data_route_blocks_final_write(self):
        data = completion_for("eightdegrees-communication-context-process")
        result = next(r for r in data["completion"]["checks"] if r["name"] == "route")
        result.update(exit_code=2, result={"status": "NeedsCorrection"})
        self.assertEqual(CHECKS.owner_write(data)["status"], "Deferred")

    def test_current_invocation_and_revision_cannot_be_swapped(self):
        for key in ("invocation_id", "publication_version"):
            data = completion_for("eightdegrees-initialization"); data["registry"][key] = "other"
            self.assertEqual(CHECKS.owner_write(data)["status"], "Deferred")

    def test_route_policy_owner_and_version_are_bound_to_the_owner_contract(self):
        for field, value in (("owner", "eightdegrees-email-scanning"), ("policy", "one-cycle-no-customer-send"), ("content_version", "old-version")):
            data = completion_for("eightdegrees-communication-context-process")
            next(r for r in data["completion"]["checks"] if r["name"] == "route")["result"][field] = value
            self.assertEqual(CHECKS.owner_write(data)["status"], "Deferred")

    def test_action_proof_from_another_task_or_version_is_rejected(self):
        for field, value in (("task_page_id", HUB), ("content_version", "old-version")):
            data = completion_for("eightdegrees-communication-context-process")
            next(r for r in data["completion"]["checks"] if r["name"] == "action")["result"][field] = value
            self.assertEqual(CHECKS.owner_write(data)["status"], "Deferred")

    def test_missing_task_versions_or_active_page_bindings_block_completion(self):
        for field in ("task_versions", "action_bindings"):
            data = completion_for("eightdegrees-communication-context-process"); data["registry"][field] = {}
            self.assertEqual(CHECKS.owner_write(data)["status"], "Deferred")

    def test_final_owner_success_log_uses_same_guard(self):
        data = completion_for("eightdegrees-initialization")
        data["call"] = {"tool": "mcp__codex_apps__notion_notion_create_pages", "args": {
            "parent": {"data_source_id": LOGS}, "pages": [{"properties": {"Result": "Success", "Phase": "Result"}}]}}
        self.assertEqual(CHECKS.owner_write(data)["status"], "WithinOwnerScope")
        data["completion"]["checks"][0]["exit_code"] = 1
        self.assertEqual(CHECKS.owner_write(data)["status"], "Deferred")

    def test_customer_send_completion_needs_exact_stored_draft_check(self):
        data = completion_for("eightdegrees-sales-reply", "SendApprovedReply")
        data["registry"]["resume_step"] = "SendApprovedReply"
        self.assertEqual(CHECKS.owner_write(data)["status"], "Deferred")
        reply = fixture(); reply["manifest"].update(task_page_id=TASK, content_version="test-v1")
        spec = {"kind": "reply-draft", "entity_id": TASK}
        data["registry"]["required_checks"]["mail"] = spec
        data["completion"]["required_checks"]["mail"] = spec
        data["completion"]["checks"].append({"name": "mail", "invocation_id": "run-1", "publication_version": "publication-v1",
                                            "exit_code": 0, "result": ADAPTER.verify(reply)})
        self.assertEqual(CHECKS.owner_write(data)["status"], "Deferred")
        sent = copy.deepcopy(reply); sent.update(phase="sent", sent_message_id="sent-1")
        sent["message"].update(id="sent-1", label_ids=["SENT"])
        spec_sent = {"kind": "reply-sent", "entity_id": TASK}
        data["registry"]["required_checks"]["sent"] = spec_sent
        data["completion"]["required_checks"]["sent"] = spec_sent
        data["completion"]["checks"].append({"name": "sent", "invocation_id": "run-1", "publication_version": "publication-v1",
                                            "exit_code": 0, "result": ADAPTER.verify(sent)})
        self.assertEqual(CHECKS.owner_write(data)["status"], "Deferred")
        from test_scheduled_outcomes import RECEIPT, OUTCOME, receipt_input, note_readback, saved_outcome
        receipt = receipt_input()
        manifest = reply['manifest']
        for key, value in {'sender': manifest['from_address'], 'recipient': manifest['to'],
                           'subject': manifest['subject'], 'payload_sha256': manifest['html_sha256']}.items():
            receipt['approved'][key] = receipt['sent'][key] = value
        receipt['note_readback'] = note_readback(receipt)
        for name, kind, result in [('outcome', 'outcome', OUTCOME.verify_projection(saved_outcome())),
                                   ('receipt', 'crm-receipt', RECEIPT.verify(receipt))]:
            spec = {'kind': kind, 'entity_id': TASK}
            data['registry']['required_checks'][name] = spec
            data['completion']['required_checks'][name] = spec
            data['completion']['checks'].append({'name': name, 'invocation_id': 'run-1',
                'publication_version': 'publication-v1', 'exit_code': 0, 'result': result})
        self.assertEqual(CHECKS.owner_write(data)["status"], "Deferred")
        from test_material_handoff import inputs as handoff_input, saved
        import material_handoff
        handoff = handoff_input(); handoff['email_task_id'] = TASK
        handoff['event']['message_id'] = 'sent-1'
        result = material_handoff.verify({'input': handoff,
            'saved_email_task': saved(handoff, 'email') | {'id': TASK}, 'saved_cycle': saved(handoff)})
        spec = {'kind': 'material-handoff', 'entity_id': TASK}
        data['registry']['required_checks']['handoff'] = spec
        data['completion']['required_checks']['handoff'] = spec
        data['completion']['checks'].append({'name': 'handoff', 'invocation_id': 'run-1',
            'publication_version': 'publication-v1', 'exit_code': 0, 'result': result})
        self.assertEqual(CHECKS.owner_write(data)["status"], "WithinOwnerScope")
        for field, value in [('message_id', 'another-message'), ('content_version', 'old-version')]:
            bad = copy.deepcopy(data)
            next(r for r in bad['completion']['checks'] if r['name'] == 'handoff')['result'][field] = value
            self.assertEqual(CHECKS.owner_write(bad)['status'], 'Deferred')
        bad = copy.deepcopy(data)
        next(r for r in bad['completion']['checks'] if r['name'] == 'outcome')['result']['action_page_id'] = 'f' * 32
        self.assertEqual(CHECKS.owner_write(bad)['status'], 'Deferred')
        bad = copy.deepcopy(data)
        next(r for r in bad['completion']['checks'] if r['name'] == 'receipt')['result']['message_id'] = 'another-send'
        self.assertEqual(CHECKS.owner_write(bad)['status'], 'Deferred')
        bad = copy.deepcopy(data)
        next(r for r in bad['completion']['checks'] if r['name'] == 'receipt')['result']['content_version'] = 'old-version'
        self.assertEqual(CHECKS.owner_write(bad)['status'], 'Deferred')
        next(r for r in data['completion']['checks'] if r['name'] == 'mail')['result']['phase'] = 'sent'
        self.assertEqual(CHECKS.owner_write(data)["status"], "Deferred")

    def test_receipt_only_recovery_binds_current_outcome_without_replaying_mail(self):
        from test_scheduled_outcomes import RECEIPT, OUTCOME, receipt_input, note_readback, saved_outcome
        data = completion_for('eightdegrees-sales-reply', 'RecordSendReceipt')
        receipt = receipt_input(); receipt['note_readback'] = note_readback(receipt)
        for name, kind, result in [('outcome', 'outcome', OUTCOME.verify_projection(saved_outcome())),
                                   ('receipt', 'crm-receipt', RECEIPT.verify(receipt))]:
            spec = {'kind': kind, 'entity_id': TASK}
            data['registry']['required_checks'][name] = spec
            data['completion']['required_checks'][name] = spec
            data['completion']['checks'].append({'name': name, 'invocation_id': 'run-1',
                'publication_version': 'publication-v1', 'exit_code': 0, 'result': result})
        self.assertEqual(CHECKS.owner_write(data)['status'], 'WithinOwnerScope')
        data['completion']['checks'][-1]['result']['message_id'] = 'different-send'
        self.assertEqual(CHECKS.owner_write(data)['status'], 'Deferred')

    def test_cli_no_contract_has_nonzero_exit_and_no_side_effect(self):
        data = completion_for("eightdegrees-initialization"); del data["completion"]
        result = subprocess.run([sys.executable, "-B", str(SCRIPTS / "notion_checks.py"), "owner-write", "--input", "-"],
                                input=json.dumps(data), text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["status"], "Deferred")


if __name__ == "__main__":
    unittest.main()
