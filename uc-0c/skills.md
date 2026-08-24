skills:
  - name: load_dataset
    description: Reads CSV, validates columns, reports null count and which rows before returning.
    input: string (file path to input CSV)
    output: dictionary containing the validated rows and a list of identified null rows.
    error_handling: Do not silently remove nulls; log their existence and retain them in the dataset for explicit flagging.

  - name: compute_growth
    description: Takes ward, category, growth_type, returns per-period table with formula shown.
    input: loaded dataset, string (ward), string (category), string (growth_type)
    output: table/list of dictionaries containing period, actual spend, growth percentage, and formula explicitly stated.
    error_handling: Return refusal string if aggregation across wards is attempted or if growth_type is absent.
