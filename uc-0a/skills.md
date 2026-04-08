# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint row to assign category, priority, and reason based on text description.
    input: Dictionary containing complaint details, specifically the 'description' string.
    output: Dictionary with keys 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: If description is null, ambiguous, or unmatchable, category is set to 'Other' and flag set to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint iteratively, and outputs a combined results CSV.
    input: input_path (string) and output_path (string) to CSV files.
    output: Writes parsed elements with appended category, priority, reason, and flag columns arrayed in CSV format.
    error_handling: Skips completely malformed rows and flags rows providing inadequate data with NEEDS_REVIEW without crashing.
