# skills.md — UC-0C

skills:

load_dataset:
  description: >
    Load ward budget CSV data and validate structure.

  inputs:
    - file_path

  validation:
    required_columns:
      - period
      - ward
      - category
      - budgeted_amount
      - actual_spend
      - notes

  actions:
    - read CSV
    - count total rows
    - detect null rows in actual_spend
    - report which rows contain nulls
    - return dataframe

  output:
    dataset
    null_row_list


compute_growth:
  description: >
    Calculate MoM or YoY growth for a specific ward and category.

  inputs:
    - dataset
    - ward
    - category
    - growth_type

  steps:
    1 filter dataset by ward
    2 filter dataset by category
    3 sort by period
    4 detect null rows
    5 compute growth for valid rows only
    6 attach formula to each row

  growth_formula:

    MoM:
    ((current_actual - previous_actual) / previous_actual) * 100

    YoY:
    ((current_actual - last_year_actual) / last_year_actual) * 100

  null_policy:
    if actual_spend is null:
      growth = "FLAGGED"
      formula = "Not computed due to null actual_spend"
      flag = notes column

  output:
    per-period growth table