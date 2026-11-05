# Human-readable customer pages

`Clients` is a human navigation index. Its child page title is a display label, not a CRM identity key. Resolve/reuse the original customer page by verified LocationId + ContactId and registered Notion page ID; never match, merge or create customers by page title.

## Display title

- Default to the verified CRM full/display name, preserving the supplied spelling and any TEST marker. Example: `Alex Harper [TEST]`, not the full `LocationId:ContactId` string. Do not invent a name from an email address, infer a preferred name or use a test batch ID as a real name.
- When known customers have the same name, append a verified email, for example `Alex Harper - alex@example.com`; use a verified phone if email is unavailable. Disambiguate the affected generated titles consistently when their mappings are known. Do not assume shared names/emails identify one contact.
- If name and email/phone still collide across CRM locations, include the verified business/location display name, then a short contact-ID suffix only if still necessary. Do not expose full technical IDs as the primary title.
- For missing CRM names, apply [inquiry name precedence](inquiry-intake.md) using source-backed signature then From display name without CRM writes. Only when none exists, use a localized `Name to confirm - <short contact suffix>` until a real name is provided. This is a presentation fallback, not permission to guess identity or create a CRM contact. Do not block an otherwise verified communication solely for a missing display name.

## Identity metadata and registration

Keep ClientId (`LocationId:ContactId`), LocationId, ContactId, verified CRM name/contact details, source and verification time in the customer page's properties when supported. For an ordinary child page without custom properties, use a small clearly labeled metadata table in its body. Technical IDs remain available for troubleshooting without dominating the Clients index.

Register each mapping under RunSettings `client_pages`, keyed by exact ClientId, containing the actual page_id, display_title, title_source (`CRMGenerated` or `Operator`), last_generated_title and verification evidence. Keep Communications/ClientPersona child IDs with that registration when known. Do not fabricate properties on an ordinary page or rely on a rendered index label for future lookup. Existing approved Notes retain their original customer snapshot.

Examples of customer-facing navigation:

```text
Aimore/
  Clients/
    Alex Harper [TEST]/
      Communications
      ClientPersona
    Sam Lee - sam@example.com/
      Communications
      ClientPersona
```

These are illustrative display labels, not real client records or folder permissions.

## Existing pages and name changes

During an explicitly requested init upgrade, inspect registered client pages within the authorized customer tree. Verify the stored mapping against CRM before renaming legacy pages titled exactly ClientId or ContactId. Change only the original page's title and its display registration; preserve page IDs, children, source links, tasks, decisions and history. Never recreate/move a customer tree to implement a rename, and never write a Notion display-title change back to CRM.

If the registration is missing, recover it from exact existing metadata and CRM evidence, not title/name similarity; ambiguous mapping stays pending. Do not sweep unrelated private pages. If CRM name access is unavailable, retain the current page and record presentation migration pending rather than inventing a name.

For later verified CRM name changes, update a generated title in place when the current title still matches last_generated_title. If an operator has supplied/customized the title, retain it as title_source=Operator; do not repeatedly overwrite it. Rename only when explicitly requested. A title change never changes ClientId, authorizes customer matching, invalidates a decision by itself or rewrites historical approved payloads.
