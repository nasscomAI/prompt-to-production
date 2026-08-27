# skills.md

skills:
  - name: load_dataset
    description: Opens the specified CSV file, validates the requested ward/category headers, and checks for explicit `actual_spend` nulls, returning a safe structured list.
    input: Dictionary with `filepath`, `ward`, and `category`.
    output: List of dictionaries representing valid matching rows, incorporating `notes` if the row has a null.
    error_handling: System refusal raised if `ward` or `category` indicates "Any" or "All". 

  - name: compute_growth
    description: Iterates sequentially (e.g. month-to-month) through the filtered list, calculating the percentage change, handling explicit nulls by marking the outcome as NULL, and outputting the exact calculation formula.
    input: List of structured row dictionaries and a string indicating the `growth_type` (e.g., "MoM").
    output: A list of dictionaries with added keys for `mom_growth`, `formula`, and `flag`.
    error_handling: Return NULL for growth and flag accordingly if the growth type is unrecognized, or if either the current or previous period is null.
