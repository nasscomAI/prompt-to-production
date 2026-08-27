# skills.md
# UC-0C — Number That Looks Right

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates expected columns, and pre-screens for null values.
    input: File path to the raw budget CSV.
    output: A validated, filtered list of dictionary records per ward/category, along with a report of null instances.
    error_handling: Refuses to process if columns are missing or if invalid aggregation parameters are provided.

  - name: compute_growth
    description: Takes specific granular data and calculates period-over-period growth with explicit formula transparency.
    input: Pre-filtered dataset for a single ward and category, along with the specified growth_type string.
    output: A formatted CSV output containing explicit formulas, un-aggregated period rows, and strict flagging of nulls.
    error_handling: Refuses to silently drop nulls or guess the growth formula if the arguments are missing.
