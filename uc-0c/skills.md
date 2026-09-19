skills:
  - name: load_dataset
    description: Reads the budget CSV, validates the required columns, and reports the null actual_spend rows (with reasons) before returning the data.
    input: File path string to ward_budget.csv (columns period, ward, category, budgeted_amount, actual_spend, notes).
    output: Tuple of (list of row dictionaries, list of null rows with period, ward, category and reason); the null count and rows are also printed.
    error_handling: Raises a clear error if a required column is missing; treats blank/NULL actual_spend as null and non-numeric values as invalid and null; never drops or fills rows.

  - name: compute_growth
    description: Takes one ward, one category and a growth type and returns a per-period table with the formula shown in every row.
    input: List of row dictionaries from load_dataset, plus ward (string), category (string) and growth_type (MoM or YoY).
    output: List of per-period rows with ward, category, period, actual_spend, growth_type, growth_pct, formula (with numbers inserted) and flag.
    error_handling: Refuses if ward, category or growth_type is missing, is an aggregate word such as 'all', or is unknown; rows with a null actual_spend, a null base period, a missing base period or a zero base are flagged and not computed.