# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV file, filters exactly for the provided ward and category, checks structural validity, and identifies which rows contain nulls before returning the targeted dataset.
    input: The file path to the CSV, the target ward string, and target category string.
    output: A list of dictionary records containing only the exact matches for that ward and category, sorted by period.
    error_handling: Raise an exception refusing aggregation if ward or category is missing or set to 'All'. If the file is missing, fail clearly.

  - name: compute_growth
    description: Iterates over the targeted records to compute the growth metric period-over-period. It flags nulls with their notes and embeds the formula type used.
    input: The filtered dataset list from load_dataset, and the required growth_type string (e.g., 'MoM', 'YoY').
    output: A newly formatted list of records ready for CSV output, containing the new growth calculations and flags.
    error_handling: Raise an exception if growth_type is not provided. If a current or previous period is null, output 'Must be flagged — [notes]' instead of a number.
