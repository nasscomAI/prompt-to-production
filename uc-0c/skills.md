# skills.md

skills:
  - name: calculate_growth
    description: Reads budget CSV, filters to specified ward and category, calculates month-over-month growth rates for actual_spend, and writes results to CSV.
    input: Input file path (string), ward name (string), category name (string), growth type (string, e.g., 'MoM'), output file path (string).
    output: None (writes a CSV file with period, growth_rate, notes).
    error_handling: If the specified ward or category has no matching data, or if there are insufficient data points for growth calculation, output an error message to the file or raise ValueError.
