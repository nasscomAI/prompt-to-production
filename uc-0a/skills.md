# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint to determine its category, priority, and justification.
    input: A dictionary containing complaint data (at minimum a 'description' field).
    output: A dictionary with keys 'category', 'priority', 'reason', and 'flag'.
    error_handling: If the description is missing or empty, assign category 'Other', priority 'Standard', and flag 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Processes an entire CSV file of complaints and writes the results to a new CSV.
    input: Paths to the input CSV file and the output destination.
    output: A CSV file containing all original data plus 'category', 'priority', 'reason', and 'flag' columns.
    error_handling: Must not crash on malformed rows; should flag problematic rows and continue processing.
