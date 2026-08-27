# skills.md

skills:
  - name: load_dataset
    description: Reads budget CSV, validates columns, and reports all null actual_spend rows with notes before returning structured records.
    input: File path input_path (string path to ward_budget.csv).
    output: Tuple containing list of row records and list of null row report entries.
    error_handling: Raises FileNotFoundError if CSV missing; flags missing columns or unexpected data types.

  - name: compute_growth
    description: Computes period-over-period (MoM or YoY) growth for a specific ward and category, outputting formatted records with explicit formula strings.
    input: Records list, ward name, category name, and growth_type ('MoM' or 'YoY').
    output: List of dictionaries with keys period, ward, category, budgeted_amount, actual_spend, growth_pct, formula, notes.
    error_handling: Refuses if ward, category, or growth_type is missing; marks rows following null periods as uncomputable with an explicit reason.
