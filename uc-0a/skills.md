# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint to determine its category, priority, and justification.
    input: A string containing the complaint description.
    output: A dictionary containing 'category' (taxonomy string), 'priority' (Urgent/Standard/Low), 'reason' (justification sentence), and 'flag' (NEEDS_REVIEW or blank).
    error_handling: If the description is empty or nonsense, returns category: Other and flag: NEEDS_REVIEW.

  - name: batch_classify
    description: Processes an entire CSV file of complaints and writes the results to a new CSV.
    input: Path to an input CSV file containing a 'description' column.
    output: Path to the generated output CSV file with added classification columns.
    error_handling: Validates file existence and column presence; skips rows that cause processing errors and logs them.
