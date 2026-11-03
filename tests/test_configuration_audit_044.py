"""Business setup visibility must not manufacture scope/consent or a runtime gate."""
import copy,unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'plugins/eightdegrees-sales-workflow/scripts'))
import configuration_audit
from test_email_presentation import page

class ConfigurationAudit(unittest.TestCase):
 def fixture(self):
  return {'customer_setup':{'operator_name':'Alex Operator','operator_id':'stable-id',
    'notion_root_id':'a'*32,'workspace_language':'en','gmail_account':'operator@example.com',
    'allowed_label_ids':['UNREAD'],'mail_scope':{'since':'2026-11-03T00:00:00Z'},
    'dropbox_work_folders':['/Authorized/Project'],'sender_account':'sender@example.com',
    'signature':'Regards, Alex','crm_location_id':'location'},
    'dropbox':{'work_folders':['/Authorized/Project']},'scanned_label_id':'progress-label'}
 def test_shows_all_saved_values_without_new_consent_or_gate(self):
  s=self.fixture();old=copy.deepcopy(s);r=configuration_audit.audit({'settings':s})
  self.assertEqual(r['missing_required'],[]);self.assertFalse(r['runtime_gate'])
  self.assertTrue(all(not f['confirmed_this_deployment'] for f in r['fields']))
  self.assertEqual(s,old)
  self.assertIn('UNREAD',r['notes'][1]);self.assertIn('not a dedicated inquiry',r['notes'][1])
 def test_missing_scope_is_not_all_mail_and_does_not_guess_operator(self):
  r=configuration_audit.audit({'settings':{}})
  self.assertIn('operator_name',r['missing_required'])
  self.assertIn('gmail_read_labels',r['missing_required'])
  self.assertIn('dropbox_authorized_folders',r['missing_required'])
  self.assertFalse(r['runtime_gate'])
  self.assertTrue(all(f['value'] is None for f in r['fields']))
 def test_conflicting_folders_are_never_silently_unioned(self):
  s=self.fixture();s['dropbox']['work_folders']=['/Other/Private']
  r=configuration_audit.audit({'settings':s});issue=r['issues'][0]
  self.assertEqual(issue['canonical_value'],['/Authorized/Project'])
  self.assertEqual(issue['legacy_value'],['/Other/Private'])
  self.assertEqual(s['customer_setup']['dropbox_work_folders'],['/Authorized/Project'])
 def test_current_label_catalog_mismatch_is_scoped_not_a_global_stop(self):
  s=self.fixture();capture={'labels':[{'id':'different','name':'Actual inbox'}]}
  r=configuration_audit.audit({'settings':s,'gmail_labels_capture':capture})
  self.assertEqual(r['issues'][0]['scope'],'New Gmail discovery only')
  self.assertFalse(r['runtime_gate']);self.assertNotIn('scan_control',s)
 def test_progress_label_cannot_be_mistaken_for_inquiry_authorization(self):
  s=self.fixture();s['customer_setup']['allowed_label_ids']=['progress-label']
  r=configuration_audit.audit({'settings':s})
  self.assertTrue(any('checkpoint label' in i['reason'] for i in r['issues']))

if __name__=='__main__':unittest.main()
