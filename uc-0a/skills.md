# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint description to assign a category and determine priority based on safety triggers.
    input: Raw text string containing the complaint description.
    output: Structured object containing 'category' (exact string from taxonomy), 'priority' (Urgent/Standard/Low), 'reason' (citation), and 'flag' (NEEDS_REVIEW or blank).
    error_handling: If text is ambiguous, outputs category 'Other' and flag 'NEEDS_REVIEW'; defaults to 'Standard' priority if no urgent keywords are present.

  - name: batch_classify
    description: Iterates through a CSV file of complaints, applying the classify_complaint skill to each row and saving the structured results.
    input: Path to the input CSV file containing raw complaint descriptions.
    output: A CSV file located at the specified output path containing the original data plus classification columns.
    error_handling: Gracefully handles missing input files and skips/logs individual row processing errors to ensure completion.
