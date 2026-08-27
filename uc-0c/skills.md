skills:
  - name: load_dataset
    description: Loads the ward budget CSV, validates the required columns, and reports rows with null actual_spend values.
    input: Path to ward_budget.csv.
    output: A list of row dictionaries plus metadata about null rows.
    error_handling: Raise a clear error if required columns are missing or the file cannot be read.

  - name: compute_growth
    description: Filters the dataset to one ward and one category, then computes period-by-period growth for the requested formula.
    input: Dataset rows, ward string, category string, and growth_type string.
    output: A per-period table with actual spend, comparison baseline, formula text, growth percentage, status, and note.
    error_handling: Refuse missing or aggregate scope requests, and flag rows where growth cannot be computed because the current or prior value is null or unavailable.
