# Project material cache

Use scripts/project_cache.py through local_checks project.cache-* operations.
The default cache is private local user state at
~/.local/state/eightdegrees/project-cache, outside the immutable plugin/repo.
It is distributed as code only: no customer files, account IDs or cached data
ship in the marketplace or Skill Pack. Windows and Linux use their actual user
home; no service, scheduler, credentials or connector is installed.

scope contains actual workspace_id, Dropbox account_id (or verified namespace
identity) and current authorized_roots using Dropbox display paths. Scope changes
or revocation produce a different cache namespace. Never reuse a cache from a
different account/workspace or union old authorization roots. If host-local
storage is unavailable, use one fresh scoped source fetch for that inquiry;
record cache unavailable, without blocking drafts or provisioning a backend.

project contains name, exact lot string and optional explicit aliases. Files
contain actual id, path, version, optional rev/effective_date, and successfully
read text. facts contains extracted project facts; fact_sources maps each key
to one or more actual file IDs. Validate/extract once on refresh, retaining raw
source text and null unknowns. A cached fact is not customer permission.

- project.cache-put: store this parsed project snapshot; ttl_seconds defaults to
  86400 (24 hours), configurable from 60 seconds to seven days. It returns a
  content-addressed snapshot_id. Old immutable snapshots remain for reviews.
- project.cache-match: use scope, name and optional exact lot. A unique match is
  ProjectMatched; a missing/ambiguous match is NeedsProjectSelection, never a
  fuzzy substitution for a different lot. Pass registered_projects from current saved settings as well, so an uncached known project can resolve and warm without a human-selection task. Model extraction is done once.
- project.cache-get: use scope/project, optional fields and include_file_ids.
  A ProjectCacheHit returns requested parsed facts and source metadata; raw
  text is returned only for selected files such as a requested source excerpt. No
  Dropbox calls or model re-extraction. Expired/missing/corrupt cache asks for
  one affected refresh, never invents empty facts or silently uses stale data.
- project.cache-invalidate: explicit material refresh or an observed source
  change removes only this project's current pointer, preserving old snapshots.
- project.cache-catalog: local directory/project/lot/alias navigation only.

Refresh only after TTL, explicit refresh, an actual observed new file/revision,
authorized scope change or local cache failure. Do not query Dropbox metadata
on every hit merely to validate the cache; that defeats this policy. When an
update is already observed, expected_revisions lets get reject the affected
snapshot immediately. Never poll every project on every mail scan.

Read current stop/approval/attempt/mail-scope inputs separately; never cache them,
customer CRM identity/persona records or sending authority here. An approved
email retains its frozen source_snapshot_id and exact content; a refresh does
not replace its payload. A known material revision can invalidate a not-yet-sent
approval and open one new combined review. TTL expiry alone does not regenerate
an already frozen approved package inside its authorized send window.
