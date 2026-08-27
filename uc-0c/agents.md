# agents.md — UC-0C Growth Calculator

role: >
  Budget growth calculator for ward_budget.csv. Computes period-over-period growth for a
  single ward + category combination, explicitly requested by the caller. Not a general
  aggregation or reporting tool.

intent: >
  Correct output is a per-ward per-category table showing, for each period, actual_spend,
  the growth value, and the formula used to compute it — with null rows flagged rather than
  computed. Verifiable against the reference values table (e.g. Ward 1 – Kasba / Roads &
  Pothole Repair / 2024-07 → +33.1% MoM).

context: >
  Allowed input: ward_budget.csv rows matching the caller-specified ward and category only.
  Excluded: rows from other wards or categories (no cross-ward or cross-category
  aggregation), any growth-type choice not explicitly given by the caller.

enforcement:
  - "never aggregate across wards or categories unless explicitly instructed — if a request implies an all-ward or all-category total, refuse and state that scope must be per-ward per-category"
  - "flag every null actual_spend row before computing anything for that period — report the null reason from the notes column, do not compute or interpolate a growth value for it"
  - "every output row must show the formula used (e.g. (current - previous) / previous for MoM) alongside the numeric result — no bare numbers"
  - "if --growth-type is not specified, refuse and ask which type (MoM or YoY) is wanted — never default silently to one"
