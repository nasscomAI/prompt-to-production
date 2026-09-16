skills:
  - name: load_dataset
    description: Ingests the budget CSV file, validates schema columns, detects missing/null actual_spend values, and generates a structured null report citing the notes column.
    input: File path (str) to ward_budget.csv.
    output: Dictionary with full dataset rows (list of dicts) and a list of identified null rows with period, ward, category, and notes.
    error_handling: Raises FileNotFoundError if missing, ValueError if required columns (period, ward, category, actual_spend) are missing.

  - name: compute_growth
    description: Computes period-over-period percentage growth (MoM) for a specific ward and category, outputting the numerical result, status flags, and the explicit calculation formula.
    input: Filtered rows for given ward and category, and growth_type (str, e.g. 'MoM').
    output: List of dictionaries with period, ward, category, actual_spend, previous_spend, growth_pct, formula, and notes/flags.
    error_handling: Refuses all-ward aggregation; sets growth to NULL when actual_spend is missing in current or previous period without dropping rows.
