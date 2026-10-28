# 0.1.5 missing-data input and workspace language

DataCompletion tasks now use a task-specific editable form in the original page body and an InputSubmitted checkbox. Required, optional and conditional fields are explicit; long answers get native paragraph sections. Preserve legacy OperatorInput, IDs, Mode and history. Untemplated legacy tasks keep their prior behavior until explicitly upgraded. A submitted task is validated before application; incomplete data returns specific corrections. Submission does not approve content, customer sends or Manual-task execution.

Initialization asks Chinese or English and persists workspace_language (zh-CN/en). A saved choice is reused. This controls user-facing workspace text, not schema names or customer-message language. Runtime instructions remain English.

The upgrade is additive to settings schema 2 and pilot-v1. Installing an updated package does not itself migrate live Notion, enable jobs or consume approvals. Existing installations need an explicit init/upgrade to adopt forms; any separately authorized live migration is recorded in customer Notion.

Validation: marketplace schema/reference/default checks, skill validation, archive build and cross-edition shared-resource comparison. Live scanning, form submission/resume and host plugin reload require testing in the installed client; package validation does not prove them.
