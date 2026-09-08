skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates columns, scans for missing or null actual_spend values, and reports a summary of all null rows before returning clean dataset records.
    input: File path string to ward_budget.csv.
    output: Tuple or structured dictionary containing validated rows, detected wards, detected categories, and list of flagged null records with period, ward, category, and notes.
    error_handling: Verifies presence of required columns ('period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'); raises ValueError if columns are missing or file cannot be parsed.

  - name: compute_growth
    description: Calculates per-period expenditure growth (e.g. Month-over-Month) for a specific ward and category, returning a tabular dataset where every row includes actual spend, growth rate percentage, formula string, and status/flags.
    input: Structured data dictionary with arguments: ward (string), category (string), growth_type ('MoM' or 'YoY').
    output: List of ordered records per period containing period, ward, category, budgeted_amount, actual_spend, growth_type, growth_rate, formula, status, notes.
    error_handling: If ward or category is missing or requested across all wards, refuses with an explanatory error. If a null actual_spend row is encountered, flags it as 'NULL_RECORD' without attempting mathematical division, showing reason from notes.
