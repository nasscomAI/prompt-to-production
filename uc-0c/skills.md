# skills.md

skills:
  - name: load_dataset
    description: reads CSV, validates columns, reports null count and which rows before returning.
    input: Path to the input CSV file (e.g., '../data/budget/ward_budget.csv').
    output: Validated dataset (DataFrame or list of records).
    error_handling: Refuse if the file is missing or if mandatory columns (period, ward, category, budgeted_amount, actual_spend) are absent. Report the count and location of null rows.

  - name: compute_growth
    description: takes ward + category + growth_type, returns per-period table with formula shown.
    input: ward (string), category (string), growth_type (string: "MoM" or "YoY").
    output: A per-period growth table (eg:- 'growth_output.csv') with a "Formula" column alongside results. Must be a per-ward per-category table — not a single aggregated number.
    error_handling: Refuse and ask the user if growth_type is missing. Flag any null actual_spend rows as "not computed" and report the reason from the notes column.
