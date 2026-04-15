skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates required columns, and reports null counts and their reasons before returning the dataset.
    input: file path to CSV with columns period, ward, category, budgeted_amount, actual_spend, notes
    output: parsed dataset as list of dictionaries plus metadata containing total rows and null row details with ward, category, period, and notes
    error_handling: raises error if file is missing or unreadable; raises error if required columns are missing; reports all null actual_spend rows with their associated notes before returning; refuses to invent or impute missing data

  - name: compute_growth
    description: Takes a filtered dataset for a specific ward and category, applies the specified growth-type formula (MoM or YoY), and returns a per-period growth table with formula shown.
    input: parsed dataset, ward name (string), category name (string), growth_type (string: MoM or YoY)
    output: per-period table with columns period, actual_spend, growth_percentage, formula_used; one row per period after the first for MoM or after the first 12 months for YoY
    error_handling: raises error if ward or category not found in dataset; raises error if growth_type is missing or invalid; flags any null actual_spend values with notes before computing; refuses to aggregate across wards or categories; refuses to compute if growth cannot be calculated due to missing prior period data
