skills:
  - name: load_dataset
    description: Reads the municipal budget CSV file, validates required schema headers, identifies and reports null actual spend counts and their corresponding rows/reasons before returning data.
    input: file_path (str: path to ward budget CSV file, e.g. ../data/budget/ward_budget.csv).
    output: A validated dataset object/dictionary containing column metadata, row records, total row count, and a list of identified null-value records with period, ward, category, and notes reason.
    error_handling: Raises FileNotFoundError if the file does not exist; raises ValueError if required columns (period, ward, category, budgeted_amount, actual_spend, notes) are missing or if the CSV is unreadable.

  - name: compute_growth
    description: Filters budget data for a specific ward and category, calculates period-over-period growth (e.g., MoM) based on specified growth type, flags null rows, and outputs a per-period table with explicit formula citations.
    input: Validated dataset records, target ward (str), target category (str), growth_type (str: e.g. 'MoM'), and output_path (str).
    output: A structured table / CSV file containing per-period records with period, ward, category, budgeted amount, actual spend, calculated growth percentage, null status flag, and explicit formula used.
    error_handling: Refuses and raises ValueError if growth_type is unspecified or unsupported; refuses cross-ward/cross-category aggregation; flags rows with null actual spend as 'NULL - Not Computed' with the notes explanation instead of performing invalid math; raises ValueError if ward or category is not found in the dataset.
