skills:
  - name: load_dataset
    description: Loads and validates the ward budget CSV and reports null rows before analysis.
    input: "input_path:string to CSV with columns period,ward,category,budgeted_amount,actual_spend,notes"
    output: "list[dict] rows + null_report:list with period/ward/category/notes for null actual_spend"
    error_handling: "Raise a clear error if file is missing, required columns are missing, or data types are invalid."

  - name: compute_growth
    description: Computes period-wise growth for one ward and one category using requested growth_type.
    input: "rows:list[dict], ward:string, category:string, growth_type:string (MoM supported)"
    output: "per-period table with period,ward,category,actual_spend,growth_type,formula,growth_percent,status,null_reason"
    error_handling: "Refuse unsupported growth_type, refuse aggregate requests, and flag rows with null or zero denominator without silent computation."
