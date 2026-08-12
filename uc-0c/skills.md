# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: load_dataset
    description: Reads and validates the budget CSV file, reports all null actual_spend rows with reasons, and returns the cleaned dataset.
    input:
      type: file path
      format: "Path to ward_budget.csv with 300 rows covering 5 wards, 5 categories, 12 months (Jan–Dec 2024)"
      required_columns:
        - period (YYYY-MM format)
        - ward (5 wards)
        - category (5 categories)
        - budgeted_amount (float, always present)
        - actual_spend (float or blank)
        - notes (string)
    output:
      type: tuple (DataFrame, null report)
      format: "Loaded dataset and structured report of null rows with count and reasons"
      null_report_includes:
        - count of null rows
        - list of null rows with period, ward, category, and reason from notes column
    error_handling:
      - If file not found, return error with file path
      - If required columns are missing, return error listing missing columns
      - If period values do not match YYYY-MM format, return error with row numbers
      - If ward or category values are unexpected, warn but continue loading
      - If more or fewer than 5 null rows detected, report discrepancy
      - Report all 5 known null rows before returning data: (2024-03 Ward 2 Drainage, 2024-07 Ward 4 Roads, 2024-11 Ward 1 Waste, 2024-08 Ward 3 Parks, 2024-05 Ward 5 Streetlight)

  - name: compute_growth
    description: Computes monthly or yearly growth rates for a specific ward-category combination, showing formula and flagging null rows.
    input:
      type: tuple (DataFrame, ward string, category string, growth_type string)
      format: "Loaded dataset, ward name (exact match from 5 wards), category name (exact match from 5 categories), growth_type ('MoM' or 'YoY')"
      required_parameters:
        - ward
        - category
        - growth_type
    output:
      type: CSV table format
      format: "Per-period table with columns: period, actual_spend, growth_rate, formula, null_flag"
      schema:
        - period: YYYY-MM
        - actual_spend: float or "NULL"
        - growth_rate: percentage string (e.g., "+33.1%") or "NULL"
        - formula: description of calculation used (e.g., "(19.7 - 14.8) / 14.8 * 100" for MoM)
        - null_flag: "FLAGGED" if row contains null, blank otherwise
    error_handling:
      - If ward is not found in dataset, return error "Ward not found in dataset"
      - If category is not found in dataset, return error "Category not found in dataset"
      - If growth_type is not specified or empty, refuse and ask user to specify "MoM" or "YoY"
      - If growth_type is neither "MoM" nor "YoY", return error and list valid options
      - If user requests aggregation across multiple wards or categories, refuse with error "Cannot aggregate across wards or categories"
      - If actual_spend is null, set growth_rate to "NULL", set null_flag to "FLAGGED", do not compute
      - If previous period is null (cannot compute growth), set growth_rate to "NULL" and explain in formula field
      - For month 2024-01 (first month), set growth_rate to "NULL" and formula to "N/A - first month"
      - Include formula in every row for verifiability against reference values
      - Verify output against reference values: Ward 1 Kasba Roads 2024-07 should show +33.1%, 2024-10 should show −34.8%