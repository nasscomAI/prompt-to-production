# skills.md

skills:
  - name: classify_complaint
    description: Receives one citizen complaint row and accurately outputs the category, priority, reason, and flag based on schema rules.
    input: Dictionary containing complaint details, specifically the description string.
    output: Dictionary with keys 'category', 'priority', 'reason', and 'flag'.
    error_handling: Return category 'Other', flag 'NEEDS_REVIEW', and explain ambiguity in reason if input is uncertain or missing.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: File paths for input CSV and output CSV (strings).
    output: A newly written CSV file at the specified output path.
    error_handling: Flag nulls, securely handle parsing errors to not crash on bad rows, and ensure output CSV is generated even if some rows fail.
