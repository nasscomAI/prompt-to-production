# skills.md — UC-0C Budget Growth Analytics

skills:
  - name: load_dataset
    description: Ingests the municipal ward budget CSV, verifies schema completeness, and audits all null actual_spend rows.
    input: file_path (str, path to ward_budget.csv).
    output: Structured dataset object containing rows, unique wards, categories, and an audit list of identified null rows with corresponding notes.
    error_handling: Raises FileNotFoundError on missing files; flags malformed rows and validates presence of essential columns (period, ward, category, budgeted_amount, actual_spend).

  - name: compute_growth
    description: Calculates deterministic period-over-period expenditure growth (MoM/YoY) for a designated ward and category series.
    input: dataset (parsed data), ward (str), category (str), growth_type (str: 'MoM' or 'YoY'), output_path (str).
    output: CSV file containing granular rows with columns 'period,ward,category,budgeted_amount,actual_spend,growth_type,growth_pct,formula,status,notes'.
    error_handling: Refuses execution if ward, category, or growth_type is invalid or missing; halts calculation and flags 'NULL_VALUE' when previous or current period actual_spend is null.
