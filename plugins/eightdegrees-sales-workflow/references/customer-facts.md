# Customer fact semantics

Use before saving extracted customer data, applying submitted clarification,
building persona proposals or publishing confirmed snapshots. Unknown is not a
verified negative. Keep source facts, operator clarification and AI suggestions
separate, with their original source/time. Never rewrite the raw communication.

For boolean business facts use three states: ConfirmedYes/true,
ConfirmedNo/false and Unknown/null. For finance, only explicit approval supports
yes; only explicit rejection supports no. Pending, not mentioned and not confirmed
stay unknown. Do not use `bool(value)`, a missing checkbox or a default false to
derive a customer fact. Control flags such as crm_written are separate.

Use the shared [execution preflight](execution-preflight.md) for owner preparation. It calls canonical_facts: validation first, then stable Approved/Rejected/Not confirmed labels without inferring a boolean or accepting ambiguous labels. The standalone helper also supports --canonical. Preserve raw source wording separately.

Before the first source/proposal/settings write, and again before applying an
approved persona, run `python3 <plugin>/scripts/fact_checks.py --input <json>` on
the actual proposed facts. The flat observed finance representation is supported:

```json
{"finance_approved": null, "finance_status": "Not confirmed"}
```

Other boolean facts use a `facts` list with name, status, value and evidence.
Known yes/no requires source evidence; Unknown requires null. Render localized
prose from these semantics while preserving the original source text. A helper
pass checks representation, not truth or approval. Failure stays pending; do not
save an inconsistent projection and repair it later. Input acceptance alone never
confirms a persona. A corrected previously approved proposal needs its normal
new-version review; successful CRM writes are not repeated to fix a snapshot.
