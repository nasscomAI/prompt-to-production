# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV, filters for the given ward and category, validates the required columns, and explicitly reports the count and locations of any null values in the actual_spend column before returning the data.
    input: "Dictionary with properties: `filepath` (string, path to CSV), `ward` (string), and `category` (string, optional but expected for strict filtering)."
    output: "A validated list of dictionaries containing the filtered data."
    error_handling: "If the file is not found or fails validation (e.g., missing expected columns), it throws an error. If there are null values in actual_spend, it prints/logs a clear warning indicating the row and the reason from the 'notes' column but still returns the dataset for downstream handling."

  - name: compute_growth
    description: Takes the validated dataset, computes the specified growth metric (e.g., MoM) for each period, and returns a formatted table including the raw formula string used for transparency.
    input: "A filtered dataset (list of dicts) and a `growth_type` string (e.g., 'MoM')."
    output: "A finalized table containing the original columns plus the computed growth percentage and the literal formula string used."
    error_handling: "If `growth_type` is missing or unrecognized, it throws a refusal error. If actual_spend is null for a given row or the preceding reference row, it sets the Growth amount to 'NULL' and Flags the output, indicating it cannot be computed."
