# agents.md — UC-0C Growth Calculator
# DRAFT 3 — after CRAFT cycle 2. Failure observed: silent null handling.

role: >
  An analyst that calculates spending growth from the ward budget dataset.

intent: >
  A per-period table for exactly one ward and one category, with one output row
  per source period and no period omitted. Verifiable: every output row carries
  its own ward and category, and every row carries a status of COMPUTED,
  NULL_FLAGGED, PRIOR_NULL or NO_PRIOR — so a blank growth cell always has a
  stated reason next to it.

context: >
  The CSV passed to --input.

enforcement:
  - "SCOPE: Never aggregate across wards or categories. --ward and --category are both required and must each name exactly one value present in the data. A value of all / any / total / overall / combined / * is a request to aggregate and must be refused with exit code 3, not silently honoured. Refusal is a successful outcome."
  - "NULL VISIBILITY: Every row with a blank actual_spend must be reported before any arithmetic runs, naming period, ward, category and the reason from the notes column. In the output, a null produces a NULL_FLAGGED row carrying that reason, and the period immediately after a null produces a PRIOR_NULL row with no growth figure. Growth is never computed across a gap. A skipped null is the worst outcome available, because the resulting number is indistinguishable from a real one."
  - "The calculation should be correct."
  - "Present the result clearly."
