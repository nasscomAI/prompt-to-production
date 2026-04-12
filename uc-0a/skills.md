# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a citizen complaint description to determine its category, priority level, and justification.
    input: dictionary containing a 'description' field and a 'complaint_id'.
    output: dictionary containing 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: If description is missing or invalid, set category: Other, priority: Low, and flag: NEEDS_REVIEW.

  - name: batch_classify
    description: Processes a CSV file of complaints, applying classification to each row and saving the results to a new CSV.
    input: String path to input CSV, String path to output CSV.
    output: None (writes results to output CSV).
    error_handling: Skip rows that are entirely corrupt but log an error. Handle empty descriptions using classify_complaint's logic.
