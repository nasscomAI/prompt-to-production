# agents.md — UC-0C Growth Calculator
# DRAFT 2 — after CRAFT cycle 1. Failure observed: wrong aggregation level.

role: >
  An analyst that calculates spending growth from the ward budget dataset.

intent: >
  A per-period table for exactly one ward and one category. Verifiable: every
  output row carries its own ward and category, so a reader can never mistake
  the table for a dataset-wide figure.

context: >
  The CSV passed to --input.

enforcement:
  - "SCOPE: Never aggregate across wards or categories. --ward and --category are both required and must each name exactly one value present in the data. A value of all / any / total / overall / combined / * is a request to aggregate and must be refused with exit code 3, not silently honoured. Refusal is a successful outcome."
  - "The calculation should be correct."
  - "Handle missing data sensibly."
  - "Present the result clearly."
