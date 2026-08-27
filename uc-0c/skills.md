# skills.md

skills:
  - name: load_dataset
    description: >
      Reads the ward budget CSV, validates its columns, and reports the null
      count and which rows are null before any computation.
    input: Path to ward_budget.csv.
    output: A list of row dicts plus a report listing every row whose
      actual_spend is blank, together with the reason from the notes column.
    error_handling: If required columns (period, ward, category, budgeted_amount,
      actual_spend) are missing, refuse to proceed and raise an error. Always
      surface the null report before computing — never compute on a dataset
      with un-reported nulls.

  - name: compute_growth
    description: >
      Computes per-period growth for exactly one ward and one category using the
      requested growth type.
    input: The dataset from load_dataset, a single ward, a single category, and a
      growth type (MoM).
    output: A per-period table (CSV rows) for that ward and category, each row
      with period, budgeted_amount, actual_spend, the exact formula used, the
      growth percentage, and a null flag.
    error_handling: Refuse if ward/category/growth-type is missing or unknown,
      and refuse if a cross-ward or cross-category aggregation is requested.
      For null actual_spend rows, output null_flag=YES with the notes reason and
      leave the growth cell blank rather than fabricating a number.
