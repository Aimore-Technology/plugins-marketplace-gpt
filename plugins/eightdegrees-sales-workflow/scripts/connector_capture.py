"""Retain original read failures before interpretation; no retries or connector I/O."""

import copy
import hashlib
import json

from scan_cycle import timestamp
from workflow_checks import inspect_result


def normalize(data):
    if not isinstance(data.get('capture_ref'), str) or not data['capture_ref']:
        raise ValueError('Persist the original response/exception first and supply its capture reference')
    timestamp(data['observed_at'])
    original = data['response']
    if not isinstance(original, dict) or not original:
        raise ValueError('An empty serialized Error is not an original diagnostic')
    exception = original.get('exception')
    if exception is not None and (not isinstance(exception, dict) or not isinstance(exception.get('message'), str) or not exception['message']):
        raise ValueError('Thrown errors require explicit name/message; JSON.stringify(Error) loses them')
    inspection = inspect_result(original)
    if exception is not None:
        inspection = {'status': 'Error', 'category': 'ThrownException', 'message': exception['message'],
                      'diagnostics': [copy.deepcopy(exception)], 'automatic_retry': False}
    failed = original.get('isError') is True or exception is not None or inspection['status'] == 'Error'
    digest = hashlib.sha256(json.dumps(original, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()
    return {'status': 'ConnectorCaptureRecorded', 'failed': failed,
            'record_type': 'connector-capture-v1', 'capture_ref': data['capture_ref'],
            'capture_sha256': digest, 'observed_at': data['observed_at'],
            'original': copy.deepcopy(original), 'inspection': inspection,
            'scope': 'Original response or explicitly captured exception only; no inferred HTTP code, retry or send authority'}
