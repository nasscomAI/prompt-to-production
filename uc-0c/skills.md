# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates required columns, and reports the null count and exactly which rows are null before returning.
    input: input_path to ward_budget.csv (string).
    output: list of row dicts (period, ward, category, budgeted_amount, actual_spend as float or None, notes) plus a printed report of the null rows and their notes.
    error_handling: Raises a clear error if the file is missing, empty, or missing any required column. A blank/"null"/"NULL" actual_spend becomes None (never 0) so it is never silently treated as a real value.

  - name: compute_growth
    description: Computes MoM or YoY growth for one ward and one category, returning a per-period table with the formula shown on every row.
    input: the loaded rows, a ward name, a category name, and growth_type ("MoM" or "YoY").
    output: ordered per-period rows with period, ward, category, actual_spend, comparison_value, growth_type, formula, growth_pct, flag.
    error_handling: Refuses (raises) if ward/category is all/any/blank or unknown, or if growth_type is not MoM/YoY. A period with a null current or comparison value is emitted with growth_pct NULL and a flag citing the null reason — never a computed number.
