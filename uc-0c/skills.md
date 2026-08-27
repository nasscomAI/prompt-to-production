# skills.md

skills:
  - name: load_dataset
    description: Reads ward_budget.csv, validates expected columns, and reports null actual_spend rows before any computation.
    input: `--input` path to ward_budget.csv.
    output: dict with keys `rows` (list of row dicts) and `null_rows` (list of {period, ward, category, notes} for the 5 deliberate nulls).
    error_handling: If expected columns (period, ward, category, budgeted_amount, actual_spend, notes) are missing, raise a clear error naming the missing column — do not proceed with a guessed schema.

  - name: compute_growth
    description: Computes per-period growth for one ward + category, using the specified growth type, showing the formula per row.
    input: `rows` (from load_dataset), `--ward`, `--category`, `--growth-type` (MoM or YoY).
    output: list of dicts, one per period, each with `period`, `actual_spend` (or null marker), `growth_pct` (or "flagged — null input"), `formula` (string showing the calculation used).
    error_handling: If --growth-type is missing, refuse — return an error asking the caller to specify MoM or YoY rather than defaulting. If a period's actual_spend is null, output that row with growth_pct="flagged" and the notes-column reason, skipping the calculation entirely.
