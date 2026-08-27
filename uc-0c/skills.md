# skills.md

skills:
  - name: load_dataset
    description: Load and filter ward budget CSV to specified ward and category only
    input: "file_path (str), ward (str), category (str)"
    output: "filtered dataframe for that ward+category only, plus null report"
    behaviour:
      - reads CSV
      - validates columns: period, ward, category, budgeted_amount, actual_spend, notes
      - filters to only the specified ward and category
      - before returning, prints a null report: how many nulls, which periods, and their notes reason
      - raises clear error if ward or category not found in data

  - name: compute_growth
    description: Compute Month-on-Month or Year-on-Year growth for filtered data
    input: "filtered dataframe, growth_type (str: MoM or YoY)"
    output: "dataframe with columns: period, actual_spend, growth_pct, formula, flag"
    behaviour:
      - MoM: growth = (current - previous_month) / previous_month * 100
      - YoY: growth = (current - same_month_last_year) / same_month_last_year * 100
      - if current or previous value is null: set growth_pct = NaN, flag = "NULL — not computed: <notes reason>"
      - show formula string in every row
      - never aggregate — one row per period
