skills:
  - name: classify_complaint
    description: Classify a single customer complaint into a category, priority, reason, and an escalation flag.
    input: One customer complaint row (e.g. string or JSON object).
    output: A standardized JSON object containing category, priority, reason, and flag values.
    error_handling: Returns an "Unclassified" category and "Low" priority with clarification flag set to true if the input is unintelligible.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: Path to an input CSV file containing customer complaints.
    output: Writes enriched data tracking categories, priorities, and reasons to a new output CSV file.
    error_handling: Skips processing and logs an error for malformed rows while continuing to the next valid row.
