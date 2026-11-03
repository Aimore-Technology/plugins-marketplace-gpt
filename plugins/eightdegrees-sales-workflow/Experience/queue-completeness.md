# Do not hand-select the ready queue

The first 0.1.45 native cycle reported six ready events but supplied only two customer-selection candidates to scan.cycle. Later, two 600s draft phases were deferred with 100s left, while omitted 90s mail work could have fitted. Source capture/owner evidence confirmed the omission.

Use scan.queue to construct all saved ready events plus validated automatic preparation; pass queue_plan to scan.cycle so a narrowed caller list cannot hide unrelated work. scan.watches emits stable ready-task recovery records before idle detection. Waiting human tasks and future dates remain waiting; exact sending/CRM approval and unknown-attempt rules remain.

Record every ready event disposition and all remaining checkpoint pointers. Do not claim idle or blame an unfitting draft for work never supplied to the selector. Offline replay and automated tests do not replace the next actual native-cycle observation.
