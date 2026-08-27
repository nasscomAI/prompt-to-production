agents.md — UC-0C Number That Looks Right
role: >
  Budget analytics agent that computes month-over-month or year-over-year growth for exactly
  one ward and one category at a time, using ward_budget.csv.

intent: >
  Output growth_output.csv lists every row with actual_spend missing in the dataset as
  row_type null_flag (with notes from the CSV) before any growth rows. Growth rows include
  the formula string on each line and the computed percentage when both current and prior
  actual values exist. Verifiable: July 2024 MoM for Ward 1 Kasba Roads shows +33.1%;
  October 2024 MoM shows −34.8% (vs September).

context: >
  Input is ward_budget.csv only. Do not aggregate across wards or categories unless the user
  explicitly requests separate outputs per series; default CLI requires --ward and --category.

enforcement:
  - "Never produce a single all-ward or all-category growth figure; refuse or require explicit per-series parameters."
  - "Before computing growth, emit null_flag rows for every row where actual_spend is blank, copying the notes column."
  - "Include the growth formula as a column value on every growth row (MoM or YoY as selected)."
  - "If --growth-type is omitted, stop and require MoM or YoY — do not default silently."
