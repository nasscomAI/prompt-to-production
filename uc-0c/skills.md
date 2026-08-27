# skills.md

skills:
  - name: load_dataset
    description: Reads the CSV dataset, validates expected columns, counts nulls, and explicitly reports which rows have nulls before returning the data.
    input: File path to the dataset CSV (string).
    output: Loaded dataset object/DataFrame and a summary report of rows with missing `actual_spend` values.
    error_handling: Throws an error if columns are missing or if actual_spend values are missing but not flagged.

  - name: compute_growth
    description: Computes growth metrics (like MoM) for a specific ward and category, returning a per-period table that includes the growth formula used.
    input: `ward` (string), `category` (string), `growth_type` (string).
    output: Tabular data (DataFrame or list of dictionaries) containing period, actual spend, computed growth, and the formula used for each period.
    error_handling: Throws an explicit refusal error if `growth_type` is not specified, refusing to guess. Throws an error if multiple wards or categories are provided.
