# skills.md

skills:
  - name: classify_complaint
    description: Processes one complaint row and returns the classification containing category, priority, reason, and flag.
    input: A single complaint row text/description.
    output: The classification result with category, priority, reason, and flag.
    error_handling: If the complaint category is genuinely ambiguous, return category 'Other' and set flag 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint to each row, and writes the results to an output CSV.
    input: Input CSV file path containing the dataset of complaints.
    output: Output CSV file path containing the classified results.
    error_handling: Skip the row if there's a malformed csv row and log an error.
