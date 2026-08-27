skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into a standard taxonomy with urgency prioritization.
    input: Dictionary containing the 'description' (string) of the complaint.
    output: Dictionary with 'category' (string), 'priority' (string), 'reason' (string), and 'flag' (string).
    error_handling: Refuses to guess if ambiguous; sets category to 'Other' and flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV of complaints and iteratively applies the classify_complaint skill to each row.
    input: Path to the input CSV file.
    output: Path to the output CSV file containing the original data plus the 4 classified fields.
    error_handling: Skips empty rows and handles malformed CSV data by logging an error and continuing.
