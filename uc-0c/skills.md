# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates columns, filters by ward and category, and detects and reports missing values before returning the data.
    input: CSV filepath, requested ward, and requested category.
    output: A filtered list of data dictionaries corresponding to the requested slice, sorted chronologically.
    error_handling: Throws an explicit error if the data format is invalid, or if cross-ward/cross-category aggregation is requested.

  - name: compute_growth
    description: Calculates the requested growth formula (e.g., MoM) for each period in the dataset, handling nulls properly.
    input: Filtered data from load_dataset and the specified growth_type.
    output: Outputs a structured table of period, ward, category, actual spend, formula explanation, and the calculated growth.
    error_handling: If an actual_spend value is missing, the row is flagged with its notes rather than calculated. Refuses to compute if growth_type is unsupported or unstated.
