# skills.md


skills:
  - name: classify_complaint
    description: Classifies a single complaint row into a specific category and priority with a cited reason.
    input: A single complaint description string and any associated metadata.
    output: A structured object containing category, priority, reason, and flag.
    error_handling: Mark as 'Other' and set flag to 'NEEDS_REVIEW' if the complaint is genuinely ambiguous.

  - name: batch_classify
    description: Processes an entire CSV file of complaints and writes the classified results to a new CSV.
    input: Path to an input CSV file containing citizen complaints.
    output: Path to an output CSV file with added category, priority, reason, and flag columns.
    error_handling: Ensure each row is processed; log errors for malformed rows and continue.
