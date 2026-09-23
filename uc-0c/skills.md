skills:
  - name: load_dataset
    description: Reads the budget CSV dataset, validates schema and column types, logs null count, and reports which rows contain null values along with their notes.
    input: input_path (str path to ward_budget.csv)
    output: list of validated row dicts and summary of detected null records
    error_handling: Raises FileNotFoundError if missing; flags unexpected columns or corrupt records without crashing.

  - name: compute_growth
    description: Computes period-over-period expenditure growth for a single ward and category, generating formula transparency and flagging null rows.
    input: dataset (list of row dicts), ward (str), category (str), growth_type (str, e.g. 'MoM' or 'YoY')
    output: list of result dicts containing period, ward, category, budgeted_amount, actual_spend, growth_rate, formula, notes
    error_handling: Refuses cross-ward aggregation; refuses missing growth_type; tags periods with missing current or base spend as NULL with explanation.
