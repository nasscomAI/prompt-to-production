# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads the budget CSV file (ward_budget.csv), validates required columns, and identifies/logs all null actual_spend rows and reasons before returning raw records.
    input: File path input_path (str) to CSV budget file.
    output: List of row dictionaries and a list of detected null row annotations.
    error_handling: Raises FileNotFoundError if CSV file is missing; raises ValueError if required schema columns are absent.

  - name: compute_growth
    description: Filters budget rows by specific ward and category, calculates sequential percentage growth (MoM or YoY) for actual_spend, attaches exact formula strings, and preserves null notes without silent zero substitution.
    input: List of row dicts from load_dataset, ward (str), category (str), growth_type (str).
    output: List of output dictionaries containing period, ward, category, budgeted_amount, actual_spend, growth_pct, formula, and notes.
    error_handling: Refuses execution if ward, category, or growth_type is missing/unspecified; refuses cross-ward/category aggregations.
