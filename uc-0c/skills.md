# skills.md — UC-0C Budget Growth Calculator

skills:
  - name: load_dataset
    description: Reads the municipal ward budget CSV dataset, validates schema and column types, logs any null values with their notes, and returns validated records along with a null audit summary.
    input: file_path (str: path to ward_budget.csv).
    output: tuple containing records (List[dict]) and null_audit (List[dict]).
    error_handling: Raises FileNotFoundError if missing, ValueError if required columns are absent, and records all null actual_spend rows for downstream transparency.

  - name: compute_growth
    description: Computes period-by-period budget spend growth (MoM or YoY) for a designated ward and category, incorporating explicit formula strings and granular null status flags.
    input: records (List[dict]), ward (str), category (str), growth_type (str: 'MoM' or 'YoY').
    output: List[dict] containing period, ward, category, budgeted_amount, actual_spend, previous_spend, growth_percent, formula, status.
    error_handling: Flags periods with null actual_spend as NULL_ACTUAL_SPEND, flags subsequent periods as PREVIOUS_PERIOD_NULL, and handles division-by-zero or missing baseline periods explicitly.
