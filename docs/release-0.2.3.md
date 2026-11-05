# 0.2.3 — Automatic material discovery

Initialization requires authorized source folders rather than a manually assembled project catalog. `projects` may be omitted or empty; populated entries remain explicit overrides and retain source-scope validation. When the catalog is automatic, exact project/lot resolution is performed by the backend against the discovered source cache. The plugin does not duplicate that cache or send customer messages.

21 client protocol tests cover the original dispatch/review boundaries, empty project initialization and backend-owned automatic project resolution.
