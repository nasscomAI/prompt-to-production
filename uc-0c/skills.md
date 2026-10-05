skills:
  - name: load_dataset
    description: Load a budget CSV and validate that the required columns exist and that null actual_spend values are surfaced with their notes-based reasons before any computation.
    input: A CSV file with columns period, ward, category, budgeted_amount, actual_spend, and notes.
    output: A validated dataset with rows preserved, including a list of null actual_spend entries flagged with their corresponding notes reason.
    error_handling: If the file is missing, unreadable, or missing required columns, return a clear validation error and do not proceed to growth calculation.

  - name: compute_growth
    description: Compute growth for one specified ward and category using either MoM or YoY, while showing the formula for each included row and preserving null-value flags.
    input: A validated dataset, a specific ward, a specific category, and a growth type of either MoM or YoY.
    output: A growth analysis for the requested ward-category combination, including per-row formulas, computed growth values, and any flagged null actual_spend rows.
    error_handling: If the ward or category is missing, the growth type is unspecified, or the dataset is invalid, stop and return a clear error instead of guessing.
