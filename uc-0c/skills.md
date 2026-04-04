skills:
  - name: load_dataset
    description: Reads the ward budget CSV file and performs a pre-computation validation check for column integrity and null value identification.
    input:
      type: file
      format: CSV file (../data/budget/ward_budget.csv) containing period, ward, category, budgeted_amount, actual_spend, and notes.
    output:
      type: object
      format: Structured dataframe or dictionary containing row data and a detailed report of the 5 specific null rows found.
    error_handling: Identifies and reports the exact count and location of null actual_spend values; fails if the file is missing or required columns are absent.

  - name: compute_growth
    description: Calculates period-over-period growth for a specific ward and category using an explicit growth type while flagging rows where computation is impossible.
    input:
      type: object
      format: "{ ward: string, category: string, growth_type: string }"
    output:
      type: file
      format: CSV (uc-0c/growth_output.csv) with columns for Actual Spend, Growth Result, and the specific formula used.
    error_handling: Refuses to process if growth_type is missing; refuses requests for all-ward or all-category aggregations; flags null rows as "not computed" and pulls the reason from the notes column.
