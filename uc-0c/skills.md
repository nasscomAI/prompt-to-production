# Budget Analyst Skills

## load_dataset
- **Input:** Path to the `ward_budget.csv` file.
- **Task:** 
  1. Load the CSV file into a structured format.
  2. Validate columns (`period`, `ward`, `category`, `budgeted_amount`, `actual_spend`, `notes`).
  3. Identify all rows where `actual_spend` is NULL.
- **Output:** A list of data rows and a summary of null counts.

## compute_growth
- **Input:** Data rows, ward name, category name, growth type (e.g., MoM).
- **Task:** 
  1. Filter data by ward and category.
  2. Sort data by period (YYYY-MM).
  3. For each period:
     - Check if current or previous `actual_spend` is NULL.
     - If NULL, set growth to "NULL: [reason from notes]".
     - If NOT NULL, compute growth using the formula: `(current - previous) / previous * 100`.
     - Record the result along with the explicit formula used.
- **Output:** A structured list of growth results for the requested ward/category.
