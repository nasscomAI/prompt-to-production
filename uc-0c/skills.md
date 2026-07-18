skills:
  - name: load_dataset
    description: Load budget CSV, validate columns, report null count and locations before returning clean data indexed by (period, ward, category).
    input: File path to ward_budget.csv with columns {period, ward, category, budgeted_amount, actual_spend, notes}
    output: Tuple (data_dict, null_report) where data_dict = {(period, ward, category): {budgeted, actual, notes}}, null_report = list of {period, ward, category, notes, reason} for all null rows
    error_handling: If file missing, raise FileNotFoundError. If required columns missing, raise ValueError listing missing columns. If CSV parsing fails, raise ValueError with line number. Always report null count in warning before returning.

  - name: compute_growth
    description: Calculate MoM growth for a specific (ward, category) pair from loaded dataset, returning time-series with formulas shown.
    input: (data_dict from load_dataset, ward string, category string, growth_type='MoM' or 'YoY', null_report list)
    output: List of dicts {period, budgeted_amount, actual_spend, growth_percent, formula_shown, flag} where flag='NULL_MISSING' for rows with null actual_spend, growth_percent is null for null rows, formula_shown displays calculation used (e.g., 'MoM = (15.2-14.1)/14.1 = 8.1%')
    error_handling: If ward or category not in data, raise ValueError naming which doesn't exist. If growth_type not in {MoM, YoY}, raise ValueError asking user to specify. If first month of series (no prior month for MoM), output growth_percent=null with note 'First period - no prior month'. For null rows, flag as NULL_MISSING and skip computation.

