skills:
  - name: classify_complaint
    description: Processes a single complaint row to determine its exact category, priority, a short reason, and an optional review flag.
    input: A dictionary representing one complaint row (containing at least the complaint description).
    output: A dictionary containing exact values for 'category', 'priority', 'reason', and 'flag'.
    error_handling: If input format is invalid, ambiguous, or unclassifiable, it returns Category as 'Other', Flag as 'NEEDS_REVIEW', and Priority as 'Standard' unless severity keywords dictate otherwise.

  - name: batch_classify
    description: Reads an input CSV of test complaints, applies the classify_complaint skill to each row, and writes the structured results to an output CSV.
    input: input_path (string) and output_path (string).
    output: Generates a CSV file at output_path.
    error_handling: Flags nulls, does not crash on bad rows, and ensures the output file is produced even if some individual rows fail.
