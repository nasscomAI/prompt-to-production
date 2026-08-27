skills:
  - name: load_dataset
    description: Read the budget CSV file, validate that required columns are present, and identify and report any null actual_spend rows along with their corresponding notes.
    input: input_path (str to the budget CSV file).
    output: A dataset (e.g., list of dicts or DataFrame) containing validated budget data, plus a report of identified null rows and notes.
    error_handling: Raise an exception if the file cannot be read or is missing required columns. Proactively identify and register rows with null actual_spend values.

  - name: compute_growth
    description: Compute the Month-over-Month (MoM) or Year-over-Year (YoY) growth of actual spend for a specific ward and category, flagging any null months and explicitly including the mathematical formula used in the output.
    input: dataset (validated budget data), ward (str), category (str), growth_type (str, e.g., 'MoM').
    output: A list of dicts detailing period, actual_spend, growth_rate, and formula used, or a refusal message if growth_type is missing or if all-ward/all-category aggregation is requested.
    error_handling: Refuse and raise ValueError if growth_type is not specified, or if the request attempts to aggregate across all wards/categories without explicit instructions. Return flagged null entries instead of calculating growth for those periods.
