skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint to determine its category, priority, reason, and review flag based on strict enforcement rules.
    input: Dictionary containing the complaint row, specifically the 'description' and 'complaint_id'.
    output: Dictionary containing 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: If input is null, malformed, or ambiguous, it assigns category 'Other', flag 'NEEDS_REVIEW', and notes the issue in the reason field without crashing.

  - name: batch_classify
    description: Reads a CSV file of complaints, processes each row using classify_complaint, and writes the structured results to an output CSV file.
    input: String path to the input CSV file and string path to the output CSV file.
    output: Writes a CSV file to the output path. Returns nothing.
    error_handling: Skips completely unparseable rows with a warning, but continues processing the rest of the batch. Ensures the output CSV is generated even if some rows fail.
