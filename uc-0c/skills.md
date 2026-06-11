skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates the required columns, and identifies any null values in actual_spend.
    input: String path to the input CSV file.
    output: A list of dictionary objects representing the rows from the CSV file.
    error_handling: Explicitly reports the count of nulls and flags the exact rows (including the notes column) where actual_spend is missing before returning data.

  - name: compute_growth
    description: Calculates per-period growth (e.g., MoM) for a specified ward and category, appending the formula used to the output.
    input: Parsed dataset (list of dicts), String ward name, String category, and String growth_type.
    output: A per-period table (list of dicts) showing actual spend, computed growth percentage, and the explicit formula used.
    error_handling: Refuse execution if growth_type is not specified (do not guess). Refuse if asked to aggregate across multiple wards/categories without explicit instruction. Flag and report null rows instead of computing them silently.
