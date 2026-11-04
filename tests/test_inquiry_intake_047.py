import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'plugins/eightdegrees-sales-workflow/scripts'))
import inquiry_intake as intake
import local_checks


class InquiryIntakeTests(unittest.TestCase):
    def test_crm_name_overrides_other_names_without_identity_approval(self):
        result = intake.name(dict(crm_match='matched', crm_name='Alex Harper',
                                  signature_name='Ori Lynn', sender_name='Other'))
        self.assertEqual((result['customer_name'], result['name_source']), ('Alex Harper', 'CRM'))
        self.assertFalse(result['identity_approval'])
        self.assertFalse(result['crm_write_allowed'])

    def test_unmatched_signature_wins(self):
        result = intake.name(dict(crm_match='none', crm_name='Unverified',
                                  signature_name='Sam Lee', sender_name='Other'))
        self.assertEqual(result['greeting'], 'Dear Sam Lee,')

    def test_from_header(self):
        result = intake.name(dict(from_header='"Jamie Smith" <jamie@example.com>'))
        self.assertEqual((result['customer_name'], result['name_source']), ('Jamie Smith', 'Sender'))

    def test_nameless_crm_fallback(self):
        result = intake.name(dict(crm_match='matched', signature_name='Chris'))
        self.assertEqual(result['name_source'], 'Signature')

    def test_anonymous_never_guesses_email_local_part(self):
        result = intake.name(dict(from_header='someone@example.com'))
        self.assertIsNone(result['customer_name'])
        self.assertEqual(result['greeting'], 'Dear Customer,')
        self.assertTrue(result['ask_customer_name'])

    def test_ambiguous_contact_remains_ambiguous(self):
        result = intake.name(dict(crm_match='ambiguous', crm_name='Wrong', signature_name='Sam'))
        self.assertEqual(result['customer_name'], 'Sam')
        self.assertEqual(result['crm_match'], 'ambiguous')
        self.assertFalse(result['identity_approval'])

    def test_invalid_name_evidence(self):
        for name in ['a@example.com', 'Sam\nOther']:
            with self.assertRaises(ValueError):
                intake.name(dict(signature_name=name))

    def fixture(self, **changes):
        data = dict(in_authorized_scope=True, account='user@example.com',
                    message_id='original1', classification='Inquiry',
                    labels=[dict(id='label1', name='AimoreInquiry')],
                    message_label_ids=['UNREAD', 'INBOX'])
        data.update(changes)
        return data

    def test_additive_label(self):
        data = self.fixture()
        before = copy.deepcopy(data)
        result = intake.label(data)
        self.assertEqual(result['action'], 'AddLabel')
        self.assertEqual(result['add_label_ids'], ['label1'])
        self.assertEqual(result['remove_label_ids'], [])
        self.assertEqual(data, before)

    def test_existing_label_is_noop(self):
        self.assertEqual(intake.label(self.fixture(message_label_ids=['label1', 'UNREAD']))['action'], 'None')

    def test_missing_label_replans_after_creation(self):
        result = intake.label(self.fixture(labels=[]))
        self.assertEqual(result['action'], 'CreateOrReuseLabelThenReplan')
        self.assertEqual(result['add_label_ids'], [])

    def test_non_inquiry_not_labeled(self):
        for classification in ['Other', 'Uncertain']:
            self.assertEqual(intake.label(self.fixture(classification=classification))['action'], 'None')

    def test_scope_and_progress_label(self):
        for changes in [dict(in_authorized_scope=False), dict(label_name='AimoreScanned'),
                        dict(message_id=''), dict(classification='Guessed')]:
            with self.assertRaises(ValueError):
                intake.label(self.fixture(**changes))

    def test_registered_operations(self):
        self.assertIs(local_checks.OPERATIONS['inquiry.name'], intake.name)
        self.assertIs(local_checks.OPERATIONS['inquiry.label'], intake.label)
