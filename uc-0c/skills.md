skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates that all required columns are present, and reports the null count and identity of every null actual_spend row before returning the dataset.
    input: File path string pointing to a CSV file with columns period, ward, category, budgeted_amount, actual_spend, and notes.
    output: Tuple of (list of row dicts representing the full dataset, list of null-row descriptors each containing period, ward, category, and null reason from the notes column).
    error_handling: If the file is missing or unreadable, raise a FileNotFoundError with the path. If any required column is absent, raise a ValueError listing the missing columns and halt — do not proceed with partial data. If null rows are detected, report them explicitly before returning; never silently drop or impute them.

  - name: compute_growth
    description: Takes a ward, category, and explicit growth_type (MoM or YoY) and returns a per-period growth table where every row includes the period, actual_spend, computed growth value, and the formula used.
    input: Filtered list of row dicts for a single ward and category (from load_dataset), plus growth_type string which must be exactly "MoM" or "YoY" — never optional or defaulted.
    output: List of result dicts each containing period, actual_spend, growth_value (float or NULL), and formula (string showing the exact calculation applied, e.g. "(current - previous) / previous * 100").
    error_handling: If growth_type is not provided or is not one of the allowed values (MoM, YoY), raise a ValueError and REFUSE to proceed — never guess or default. If actual_spend is null for a row, set growth_value to NULL, record the null reason from the notes column, and skip computation for that row without raising an error. If the dataset contains rows from more than one ward or category, raise a ValueError and REFUSE — computation must be strictly scoped to a single ward and category.
