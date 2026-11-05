# 0.2.2 — All new incoming mail

Initialization uses `gmail.scope=all-new`; recipient and label filters are retired. An omitted starting instant defaults to now in UTC; an explicit timezone-aware instant is preserved. The backend excludes sent mail, drafts, spam and trash and classifies incoming mail. Existing Dropbox/CRM boundaries and exact-version Portal approval remain in force.

The Portal setup can discover connected account details, select Dropbox folders and suggest current project materials/lots. The plugin submits one backend command and does not implement its own scanner. This release adds two initialization contract tests to the existing 17 client tests.
