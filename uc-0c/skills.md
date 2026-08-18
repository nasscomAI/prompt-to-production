# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates columns, and reports null rows before any computation.
    input: Path to a ward_budget CSV (string), e.g. ../data/budget/ward_budget.csv.
    output: A validated dataset (records with period, ward, category, budgeted_amount, actual_spend, notes) plus the null count and the list of null rows with their notes reason.
    error_handling: Fails fast if the file is missing, a required column is absent, or values fail the README schema; refuses to proceed with unvalidated data rather than guessing.

  - name: compute_growth
    description: Computes per-period growth for one ward + category using the explicitly requested growth type, with the formula shown per row.
    input: A ward (string), a category (string), a growth type (MoM | YoY | other), and a validated dataset from load_dataset.
    output: Per-period table (period, actual_spend, growth %) with the formula used shown alongside each result, serialized to growth_output.csv.
    error_handling: Refuses if growth type is unspecified; flags any null actual_spend row with its notes reason and does not compute a value for it; refuses cross-ward or cross-category aggregation.
