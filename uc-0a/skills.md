# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Transforms a single citizen complaint row into a structured classification record.
    input: Dictionary containing a 'description' string.
    output: Dictionary with 'category', 'priority', 'reason', and 'flag' (NEEDS_REVIEW or blank).
    error_handling: Return 'Other' and 'NEEDS_REVIEW' if description is blank or category is unidentifiable.

  - name: batch_classify
    description: Orchestrates the end-to-end processing of a complaint CSV file.
    input: String path to input CSV and String path for output results file.
    output: A CSV file written to the output path containing the classified results.
    error_handling: Must not crash on individual row failures; skip or flag malformed rows and continue to completion.

