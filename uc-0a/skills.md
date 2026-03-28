skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into a rigid schema including category, priority, reason, and a review flag.
    input: A single complaint description string.
    output: A structured map/object containing 'category', 'priority', 'reason', and 'flag' string fields.
    error_handling: Return flag "NEEDS_REVIEW" and default to category "Other" or "blank" if the description is genuinely ambiguous or lacks detail.

  - name: batch_classify
    description: Reads an input CSV containing complaint rows, applies classify_complaint row by row, and writes the results to an output CSV.
    input: File path to the input CSV file.
    output: Writes a new CSV file to the specified output path with the classified columns.
    error_handling: If an individual row fails to parse or parse_complaint errors, log the failure and proceed to the next row.
