# UC-0C Financial Skills

## load_dataset
**Input**: Path to a budget CSV.
**Process**:
1. Load the CSV into memory.
2. Validate required columns: `period`, `ward`, `category`, `budgeted_amount`, `actual_spend`, `notes`.
3. Count rows.
4. Scan `actual_spend` for NULLs or empties.
5. Report NULL count and specific locations (Period/Ward/Category) and their reasons from `notes`.

## compute_growth
**Input**: Ward name, Category name, Growth type (MoM).
**Process**:
1. Filter dataset for provided Ward and Category.
2. Sort by `period`.
3. For each period (starting from the second):
   - Check if current or previous `actual_spend` is NULL.
   - If NULL → output "DATA_MISSING" and cite reason.
   - Else → Calculate: `((curr - prev) / prev) * 100`.
4. Output a table with columns: `Period`, `Actual Spend`, `MoM Growth`, `Formula`.
