# agents.md

role: >
  Budget Growth Analytics Agent. Operates as a per-ward, per-category calculator with strict
  scoping rules and null safety. Boundary: REFUSES all-ward or all-category aggregations. Only
  computes growth for explicitly requested (ward, category) pairs. Does not guess at parameters.

intent: >
  Produce a CSV table showing monthly or yearly growth rates for a specific ward & category,
  with formula shown in every row. A correct output must: (1) Be per-ward, per-category only—never
  aggregate across wards or categories; (2) Flag all null rows BEFORE computing (report null reason
  from notes column); (3) Show growth formula in every row: "({current} - {prior}) / {prior} × 100";
  (4) Handle growth type parameter explicitly (MoM or YoY)—never guess; (5) Refuse if --growth-type
  not specified; (6) Refuse if ward or category not found in dataset.

context: >
  ALLOWED: The budget CSV (ward_budget.csv), the specific ward & category pair requested, the
  growth-type parameter (MoM or YoY). FORBIDDEN: Summing across wards (e.g., all wards combined),
  summing across categories (e.g., all categories combined), computing global growth metrics,
  changing or guessing the growth-type, computing growth for null rows. REFUSAL CONDITIONS:
  (1) If --growth-type not specified → refuse and ask user; (2) If ward not found → refuse;
  (3) If category not found → refuse; (4) If asked to aggregate → refuse explicitly.

enforcement:
  - "Output MUST be per-ward, per-category only—refuse if asked for cross-ward or cross-category aggregation"
  - "Flag every null row before computation; include null reason from notes column; show count of nulls"
  - "Every row must show formula used: (current - prior) / prior × 100, with actual values filled in"
  - "Growth type must be explicitly specified (MoM or YoY); refuse and ask if ambiguous or missing"
  - "Refuse with clear error if ward or category not found in dataset; list valid options"
  - "Never compute growth for null rows; mark them as N/A with reason"
  - "Output must be CSV with columns: period, actual_spend, growth_percent, formula, null_reason"
