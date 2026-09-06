# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into a category, assigns a priority, provides a reason, and flags ambiguity.
    input: A dictionary representing a single complaint row with at least a 'description' field.
    output: A dictionary with 'complaint_id', 'category', 'priority', 'reason', and 'flag' fields.
    error_handling: If the category is genuinely ambiguous, it sets 'category' to 'Other' and 'flag' to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: Paths to the input CSV file and the output CSV file.
    output: A new CSV file at the specified output path containing classified complaints.
    error_handling: Flags nulls, does not crash on bad rows, and produces output even if some rows fail.
