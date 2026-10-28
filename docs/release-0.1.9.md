# 0.1.9 Human-readable customer navigation

Customer pages under Clients were titled with the full LocationId:ContactId key, making manual browsing confusing. Use the verified CRM display/full name as the normal page title and a verified email/phone for known same-name collisions. Use a clearly labeled missing-name fallback when needed, without inventing identity or creating contacts.

Keep exact ClientId, LocationId and ContactId in supported page properties or an ordinary-page metadata table. Register the original Notion page/child IDs in RunSettings client_pages. Display titles are navigation labels only; matching, deduplication and workflow links continue to use verified CRM IDs and Notion page IDs.

An explicitly requested init upgrade verifies legacy customer mappings and renames ID-titled pages in place. Preserve children, communications, tasks, approvals and historical approved Notes; do not write the title back to CRM. Preserve operator-customized titles and never recreate a customer tree because its name changed.

Validation: both marketplace/skill/reference/package checks, cross-edition shared-payload comparison and archive inspection. No runtime helper code changed; live new-customer/same-name/title-migration scenarios are listed in pilot acceptance and remain for the designated test session. This release does not rename current test resources or change CRM records during packaging.
