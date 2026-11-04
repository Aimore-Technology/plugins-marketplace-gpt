# One tool orchestration and one local batch per phase

Collect independent current reads in one host orchestration when available.
Keep returned objects in memory, keyed by original tool call/page/message ID.
Do not invoke a shell once per response to save active input, register a version
observation, serialize the same page again or inspect files just written.
A repeated tool title is not a business checkpoint. Do not create read/save/
observation loops while waiting for a result that was already returned.

## Normal path

1. Read the phase's affected settings/tasks/actions/messages once. Preserve
   original response objects, errors, warnings and complete pagination. Reuse
   these objects in every local check and newly ready successor in this phase.
2. Supply one small plan with named captures and all ready checks. Use
   python3 <plugin>/scripts/local_checks.py --input <phase.json> --output <result.json>.
   phase.json may contain both captures={name:original_response} and checks.
   It can also be passed with --input - as one complete stdin payload. No
   preliminary capture file or separate version-registration command is needed.
3. Inputs use {"$capture":"name"} and {"$result":"earlier-check"}. Helpers
   receive isolated original objects. Require exit 0 and LocalChecksPassed;
   inspect each actual helper status. A successful batch is not send authority.
   --output retains exact results/calls while stdout prints compact summaries.
   Execute the checked call directly from that local result; do not print its
   body, split it into shell chunks or repeatedly reconstruct it in context.
4. If originals need a durable local checkpoint, include capture.commit in that
   same phase batch, or call capture_bundle.py once with the whole phase input.
   It atomically merges originals into one private cycle bundle outside the
   plugin. Identical aliases/objects write nothing. An alias is immutable: use
   a new phase/revision alias for a genuinely changed original. This is local
   recovery data, not another Notion log, authority cache or execution identity.

capture.commit input: bundle_path (absolute private local path), root_id,
cycle_key (local cycle correlation only), observed_at with offset, captures
(nonempty named exact original response or explicit exception objects). The
result reports counts/path/fingerprints and failed diagnostics. A saved failure
still means missing coverage; it never becomes a successful read. Bundles can
be loaded with --captures <bundle.json>; plain legacy dictionaries still work.
Other invocations never reuse captured approval/stop state as current evidence.

An unchanged idle scan needs no capture checkpoint solely to report that it
checked versions. Use actual discovery fingerprints/cursors in EventIndex;
persist it only when scan.probe.persist_required is true. A changed cursor,
pending handoff, incomplete pagination or real failure still needs its recovery
record. The original incoming response is not a replacement for a durable
Inbox source required before customer processing.

## Keep business boundaries

Batching does not postpone a required durable effect boundary: save original
source/accepted decision/AttemptId before its dependent operation, and retain a
provider's accepted or unknown result immediately. One provider response can
join one result batch; it must never be resent to repair logging. Persist the
changed event index before advancing its cursors and confirm API success.

A successful own write updates the local projection from its original API
acknowledgement; it does not invalidate every captured page or trigger a new
fetch. A relevant external edit, new version, stop/reply or delayed send needs
one affected fresh observation. No saved-body/MIME/preview readback. Reuse the
same imminent accepted task/action/control observation for dispatch.

Coalesce source/task/action status at their real business boundary and cycle
metrics once at cycle close. Do not write logs for file saves, helper calls,
metadata reads or logging itself. Later errors preserve original captures and
completed effects; rerun only the affected failed check with new evidence.
No new service, native task or global execution lock is introduced.
