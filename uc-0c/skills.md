# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

load_dataset:
  description: >
    Reads the ward budget CSV file and validates the required columns.
    Reports total number of null rows and identifies which rows have null actual_spend
    before returning the dataset for further processing.
  input:
    - file_path: path to the CSV file (string)
  output:
    - dataset: cleaned and validated dataset with null rows flagged
  error_handling:
    - Refuse if required columns (period, ward, category, budgeted_amount, actual_spend) are missing
    - Flag all rows where actual_spend is null and include notes for reporting

compute_growth:
  description: >
    Computes per-period (monthly) growth for a specific ward and category
    using the specified growth_type (e.g., MoM). Includes actual spend, computed
    growth, and formula used for each row. Null rows are not computed, but flagged.
  input:
    - dataset: validated dataset from load_dataset
    - ward: string specifying ward to filter
    - category: string specifying category to filter
    - growth_type: string specifying the growth calculation type (e.g., MoM)
  output:
    - per_period_table: table with period, ward, category, actual spend, growth, formula, flagged nulls
  error_handling:
    - Refuse computation if ward/category not specified
    - Refuse if growth_type is missing or unsupported
    - Refuse if attempting aggregation across wards or categories
    - Skip growth calculation for null actual_spend rows but report them