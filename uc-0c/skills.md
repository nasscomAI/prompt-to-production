skills:
  - name: load_dataset
    description: reads CSV, validates columns, reports null count and which rows before returning
    input: file path to the CSV dataset (string)
    output: validated tabular data, total null count, and a list of rows containing nulls with their corresponding reasons
    error_handling: flags formatting errors or missing files; ensures explicit reporting of nulls before proceeding

  - name: compute_growth
    description: takes ward + category + growth_type, returns per-period table with formula shown
    input: validated dataset, ward (string), category (string), and growth_type (string, e.g., 'MoM', 'YoY')
    output: per-period table containing period, actual spend, calculated growth, and the formula used for each row
    error_handling: if --growth-type is not specified, refuse and ask; if all-ward aggregation is requested, refuse; if actual_spend is null, flag the row and do not compute
