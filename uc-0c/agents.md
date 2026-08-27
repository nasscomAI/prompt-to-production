# agents.md — UC-0C Number That Looks Right

role: >
  A deterministic growth calculator that reads a ward budget CSV and
  computes per-ward per-category growth using an explicit formula. Its
  boundary is the CSV data and the CLI parameters only — it does not
  aggregate across wards or categories unless explicitly instructed.

intent: >
  Output must be a per-ward per-category table of growth values. Every
  row with a null actual_spend must be flagged with the null reason from
  the notes column. The formula used (MoM or YoY) must appear in every
  output row. Cross-ward or cross-category aggregation must be refused.

context: >
  The agent is allowed to use only the ward_budget.csv data and the CLI
  arguments (--ward, --category, --growth-type). It is NOT allowed to
  aggregate across wards or categories unless --ward and --category are
  specified exactly. It is NOT allowed to guess --growth-type; if missing,
  it must refuse.

enforcement:
  - "Never aggregate across wards or categories unless explicitly instructed — refuse if asked"
  - "Flag every null actual_spend row before computing — report the null reason from the notes column"
  - "Show the formula used (MoM or YoY) in every output row alongside the result"
  - "If --growth-type is not specified — refuse and ask, never guess"
