skills:
  - name: load_dataset
    description: Ingests the municipal budget CSV file, validates required column schema, reports dataset summary stats (total rows, wards, categories, null count), and inventories all deliberate null actual_spend rows along with their recorded notes.
    input: file_path (str) path to ward_budget.csv.
    output: dict containing validated list of row dictionaries, set of valid wards, set of valid categories, and an inventory of null actual_spend rows.
    error_handling: Raises descriptive errors and aborts execution if the file does not exist, required columns are missing, or the CSV structure is corrupted.

  - name: compute_growth
    description: Calculates chronological period-over-period budget expenditure growth for exactly one validated ward, one category, and an explicit growth type (MoM or YoY), producing a detailed row-by-row calculation table exposing formulas, comparison values, statuses, and notes.
    input: dataset (dict from load_dataset), ward (str), category (str), growth_type (str: 'MoM' or 'YoY').
    output: list of dicts with keys period, ward, category, budgeted_amount, actual_spend, growth_type, comparison_period, comparison_actual_spend, formula, growth_percent, status, notes.
    error_handling: Refuses execution on ambiguous/all-ward requests, unknown wards/categories, or missing growth_type; flags null and non-computable rows (FIRST_PERIOD, MISSING_CURRENT, MISSING_COMPARISON, NO_PRIOR_YEAR_DATA, ZERO_DENOMINATOR) with blank growth values and explicit explanatory formula/status fields.
