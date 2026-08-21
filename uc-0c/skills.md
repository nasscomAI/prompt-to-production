# skills.md — UC-0C

skills:
  - name: load_dataset
    description: Reads CSV, validates column structures, and proactively identifies null rows by logging the note attached to the null value before execution.
    input: File path to the ward budget CSV file.
    output: A structured table/list of filtered dataset rows alongside a report of any null values mapped to their explanatory notes.
    error_handling: Halts operations if essential grouping keys like ward or category are corrupted.

  - name: compute_growth
    description: Takes the filtered list by ward, category, and standardizes a chronological growth formula (e.g., Month-over-Month).
    input: Time-sorted filtered list of spending data, and the specified growth formula identifier.
    output: Sequential growth percentage rates.
    error_handling: Returns "Must be flagged — not computed" and halts row computation if comparing against a null base or target value.
