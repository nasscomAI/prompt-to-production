# skills.md
skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into a standard category and assigns a priority.
    input: A dictionary containing complaint details, primarily 'description'.
    output: A dictionary with 'category', 'priority', 'reason', and 'flag'.
    error_handling: Returns category 'Other' and flag 'NEEDS_REVIEW' if ambiguous.

  - name: batch_classify
    description: Reads a CSV of multiple complaints, applies classify_complaint per row, and writes to an output CSV.
    input: input_path (string) and output_path (string) representing file paths.
    output: Writes a CSV file with the classification results.
    error_handling: Flags nulls, does not crash on bad rows, and produces output even if some rows fail.
