# agents.md

role: >
  A deterministic CLI agent that computes month-over-month (MoM) or
  year-over-year (YoY) spend growth for exactly one ward+category
  combination from the municipal ward budget CSV
  (../data/budget/ward_budget.csv). It is not a general budget analyst:
  it does not summarize trends, does not forecast, does not aggregate
  across wards or categories, and does not interpret or editorialize on
  the notes column. It either performs the single arithmetic operation
  requested and shows its work, or it refuses and explains why.

intent: >
  Correct output is a per-period table scoped to the single ward+category
  pair supplied via --ward and --category, written to growth_output.csv.
  Every row must contain: period, actual_spend, budgeted_amount, the
  comparison period used, the growth percentage (or an explicit null
  flag), and the literal formula with substituted numbers that produced
  that percentage. Output is verifiable directly against the reference
  values in README.md — the five listed null rows must never show a
  computed growth number, and every other row's percentage must match.

context: >
  The agent may use only: the CSV at the path given by --input, the
  columns defined in the dataset structure (period, ward, category,
  budgeted_amount, actual_spend, notes), and the single ward+category
  pair the user specified. It is explicitly excluded from: reading or
  combining rows for any other ward or category, using outside knowledge
  of municipal budgeting, inflation, or seasonal norms to explain or
  adjust figures, treating the notes column as anything other than the
  literal reason string to surface for a null row, and inventing or
  interpolating a value for a missing actual_spend. No part of this
  workflow calls a language model at runtime; compute_growth is plain
  deterministic arithmetic over structured data.

enforcement:
  - "Never aggregate, sum, or average actual_spend or budgeted_amount across more than one ward or more than one category in a single output. If the user asks for a total, combined, overall, or all-ward/all-category figure, refuse with an explicit message instead of computing anything."
  - "Before computing any growth value for a period, check both that period's row and its comparison-period row (previous month for MoM, same month prior year for YoY) for a null actual_spend. Every null row encountered anywhere in that check — target or baseline — must be flagged in the output with the exact reason text copied from its notes column."
  - "Never compute or impute a growth percentage when either the target period or its comparison baseline has a null actual_spend. Output growth_pct as 'N/A — null data' for that row instead of a number, silently skipping, or defaulting to zero."
  - "Every output row that does contain a computed growth percentage must also contain the formula field showing the literal arithmetic with real numbers substituted in, e.g. '(19.7 - 14.8) / 14.8 * 100 = +33.11%' — not just the resulting percentage on its own."
  - "If --growth-type is omitted or is not exactly one of MoM or YoY, refuse before reading or processing any data. State that growth type must be specified, list the two valid values, and exit without producing output. Never default to either type."
  - "If --growth-type YoY is requested for a period whose comparison period (12 months earlier) does not exist in the dataset, flag that row as 'N/A — no prior-year data available' rather than guessing, estimating, or falling back to MoM."
  - "If the --ward or --category value does not exactly match a value present in the dataset, refuse and list the valid ward/category values rather than guessing the closest match or silently proceeding."
