skills:
  - name: load_dataset
    description: Reads the CSV dataset, validates expected columns, and reports null count and which rows contain null actual_spend values before returning.
    input: File path to the CSV dataset (string).
    output: A structured dataset (e.g., DataFrame) and a pre-computation report detailing the count and specifics of any null actual_spend rows.
    error_handling: Raises an error if the file is missing or if the required columns are not present.

  - name: compute_growth
    description: Calculates the specified growth metric (e.g., MoM) for a given ward and category, returning a per-period table with the exact formula shown.
    input: Ward (string), category (string), and growth_type (string, e.g., 'MoM').
    output: A per-period table containing the computed growth values, with the exact mathematical formula used shown alongside each result.
    error_handling: If growth_type is omitted, refuse to calculate and ask the user to specify it. If actual_spend is null for a period, flag it without computing a value.
