# EightDegrees Sales Workflow 0.1.50

Includes the [short inquiry flow and scoped cache](release-0.1.49.md): one
content-and-send review, automatic name fallback, private 24-hour project cache,
API acknowledgement completion, standing notification SMS and reduced rule load.

Approval parsing now reads choices/submission/comments only from the original
operator input section. Checkbox-like text in an email HTML/code block cannot
supply the human decision. The existing source/task/version binding, stop,
window and accepted/unknown no-replay controls remain unchanged. No real task,
source, approval or native timer is altered by installing the package.

Validation: 665 offline tests cover both editions and the standalone pack,
including an email-body checkbox regression. Packaging and runtime-rule checks
validate the current payload; real Notion rendering, local timed cycles and
end-to-end latency still require a target-host run.
