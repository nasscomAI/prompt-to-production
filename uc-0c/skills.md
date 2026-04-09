load_dataset:
  name: load_dataset
  description: Reads CSV file, validates required columns, and reports null count and specific null rows before returning structured data
  input:
    type: string
    format: file path to CSV file with columns (period, ward, category, budgeted_amount, actual_spend, notes)
  output:
    type: structured data
    format: pandas DataFrame with validation report showing null count and which specific rows contain null actual_spend values
  error_handling: >
    If CSV file is missing required columns, return error message specifying missing columns.
    If file cannot be read, return file access error. Always report the 5 deliberate null 
    actual_spend values with their period, ward, category, and reason from notes column 
    before returning the dataset.

compute_growth:
  name: compute_growth
  description: Takes ward, category, and growth type parameters to compute period-wise growth rates with explicit formula display
  input:
    type: object
    format: ward (string), category (string), growth_type (MoM or YoY), filtered dataset
  output:
    type: CSV table
    format: per-period table with columns (period, actual_spend, growth_rate, formula_used) for the specified ward and category
  error_handling: >
    If growth_type is not specified, refuse computation and ask user to specify MoM or YoY.
    If ward or category not found in dataset, return error listing available options.
    For periods with null actual_spend, flag the row with "NULL - [reason from notes]" 
    instead of computing growth. Never aggregate across multiple wards or categories - 
    refuse if requested and explain the per-ward per-category requirement.