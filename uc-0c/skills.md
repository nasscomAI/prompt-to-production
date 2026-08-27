skills:
  - name: calculate_growth
    description: Computes exact growth percentages (e.g., MoM) for a specific ward and category. It applies the requested growth formula to each period sequentially.
    input: Filtered dataset for a single ward and category, and a required growth_type parameter.
    output: A per-period table (array of records) containing the actual spend, calculated growth percentage, and the exact formula used for each period.
    error_handling: Refuse to compute if growth_type is omitted. Refuse to aggregate across wards or categories. If a null actual_spend is encountered, flag the period, refuse to compute growth for it, and report the reason from the notes column.
  
  - name: format_growth_report
    description: Takes the computed growth table and writes it to the output CSV file in the required structure.
    input: The computed per-period growth records from calculate_growth, along with the output file path.
    output: A properly formatted CSV file written to disk.
    error_handling: Raise an error if the output file path is inaccessible or if required fields (like the formula or flag columns) are missing from the input records.
