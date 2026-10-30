# EightDegrees Sales Workflow 0.1.19 candidate

The 0.1.18 controlled run continued after a failed fact precheck and saved a
Return dependency checklist late. This change gives both editions one packaged
preparation/readback path before dependent work, while retaining the original
failures as live regressions to verify.

- execution_preflight.py prepare combines actual fact, Notion property and reply
  manifest checks. A refusal exits 2 with no usable plan or output parameters.
  Required completion checks are generated from affected resource roles, with
  declared slots for not-yet-created records. There are no connector calls.
- ready requires the exact generated plan in an actual complete owning-run fetch,
  resolves only predeclared bindings and rejects changed results/outputs, missing
  evidence, late roles and existing-target replacement. It returns an owner
  registry with a saved-plan completion obligation tied to run/digest/phase.
- Canonical fact labels are emitted only after valid three-state semantics;
  ambiguous labels and unknown-to-false changes still fail. Stored-reply header
  lists/null are refused explicitly rather than guessed into a different payload.
- All eight owners use the shared preparation path. The report remains limited
  to its own report/run/log targets. The helper is not a host MCP interceptor,
  permission source, independent runtime, lock or proof of historical call order.
- Recurring read guidance uses known saved views and preserves SQL capability
  degradation after quota refusal. One capture serves local checks within a
  phase; fresh action input and external-action guards remain mandatory.
  An unchanged canonical row does not prove an ordinary action page is unchanged.
- Four short Experience cards cover failed prechecks, frozen plans, Notion quota
  and capture reuse, without customer data or copied live reports.

## Verification and remaining acceptance

- 234 offline tests passed per edition: the preceding 210 plus 24 new regressions
  for preflight failure/order evidence, canonical values and header types.
- Marketplace/English frontmatter/reference checks and deterministic archive
  inspections passed for both editions. Shared changed business files are equal;
  edition-specific runtime, command wrappers and manifests are preserved.
- This source change does not run customer sends, CRM writes or native schedules.
  The prior live F01/F02 findings are not closed by offline helper results. See
  [directed acceptance](test-0.1.19.md) before promoting the candidate to Beta.
- No measured live latency reduction, received-message pass, cloud runtime pass
  or prevention of direct model/tool bypass is claimed.

Reviewer path: execution_preflight.py and test_execution_preflight.py first,
then execution-preflight.md and owner-completion.md, followed by the fact/header
changes and recurring read guidance. Changes affect model execution instructions
and local evidence checks, with no new credentials, permissions or backend.
