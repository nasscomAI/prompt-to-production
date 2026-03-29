skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates that all required columns are present, and reports the total null count and the exact rows with null actual_spend values before returning the dataset.
    input:
      type: file path
      format: string — absolute or relative path to a CSV file containing columns period, ward, category, budgeted_amount, actual_spend, notes
    output:
      type: structured dataset with null report
      format: parsed tabular data accompanied by a list of null rows each containing period, ward, category, and the notes value explaining the null reason
    error_handling:
      - If the file path does not exist or cannot be read, halt and return a clear error with the invalid path
      - If any required column (period, ward, category, budgeted_amount, actual_spend, notes) is missing, halt and report the missing column name
      - If the dataset contains zero rows after loading, halt and report the empty dataset error
      - Never silently skip or impute null actual_spend values — always surface them explicitly before returning

  - name: compute_growth
    description: Takes an explicit ward, category, and growth_type and returns a per-period growth table with the formula used displayed alongside every computed result.
    input:
      type: named parameters
      format: ward (string matching one of the 5 ward names), category (string matching one of the 5 category names), growth_type (string — must be one of MoM or YoY, never assumed)
    output:
      type: per-period growth table
      format: CSV or tabular rows with columns period, actual_spend, growth_value, formula, null_flag — null_flag is set and growth_value is left blank for any period where actual_spend is null
    error_handling:
      - If ward does not match any known ward name, refuse and list valid ward options
      - If category does not match any known category name, refuse and list valid category options
      - If growth_type is not provided, refuse immediately and ask the user to specify MoM or YoY — never infer or default
      - If the requested ward and category combination contains a null actual_spend row, flag that row with its notes reason before computing any other rows
      - If the caller requests aggregation across multiple wards or categories, refuse and explain that only per-ward per-category computation is permitted
