skills:
  - name: load_dataset
    description: Reads the budget CSV file using csv.DictReader, validates required columns, and identifies all null actual_spend rows along with their corresponding notes reasons.
    input: File path to input CSV (string).
    output: Tuple containing list of record dictionaries and audit list of identified null rows with notes.
    error_handling: Raises FileNotFoundError if dataset file does not exist, or ValueError if required CSV header columns are missing.

  - name: compute_growth
    description: Filters records for a specific ward and category, calculates period-over-period growth (MoM) using exact formula, attaches formula strings, and flags null spend rows.
    input: Records list, ward name (string), category name (string), growth type (string).
    output: List of formatted growth calculation dictionaries including period, actual spend, growth percentage, formula, and status/notes.
    error_handling: Refuses execution if ward or category is set to 'all'/aggregated, or if growth_type is missing/unsupported.
