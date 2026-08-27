# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into a strict taxonomy of category, priority, and assigns a reason and flag.
    input: Dictionary representing a single CSV row.
    output: Dictionary with keys complaint_id, category, priority, reason, flag.
    error_handling: Return original complaint_id with category 'Other', priority 'Standard', reason 'Error during classification', and flag 'NEEDS_REVIEW' if API fails or parsing fails.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: String path to input CSV, String path to output CSV.
    output: Writes output CSV to disk.
    error_handling: Skip completely malformed rows but continue processing the rest. Ensure output CSV is written even if some rows fail.
