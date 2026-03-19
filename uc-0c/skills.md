skills:
  - name: load_dataset
    description: Reads the CSV, validates columns, and prints a validation report explicitly listing the 5 deliberate null rows (identifying them by Ward/Category/Period) before returning records.
    input: File path (string)
    output: List of dicts
    error_handling: Refuses to proceed if file is missing or required columns (period, ward, category, budgeted_amount, actual_spend, notes) are absent.

  - name: compute_growth
    description: Implements MoM and YoY math with formula visibility; returns "NULL" and note reason for null rows; returns "N/A" for the first period.
    input: Dataset, ward, category, growth_type
    output: Formatted table with columns for Period, Spend, Growth, and Formula
    error_handling: Returns "NULL" with reason if data is missing; returns "N/A" for the first period; refuses if aggregate data is requested.

