# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint description into category, priority, reason, and flag.
    input: description (String)
    output: Dictionary with keys category, priority, reason, flag
    error_handling: Defaults to category Other and flag NEEDS_REVIEW if description is empty or indecipherable.

  - name: batch_classify
    description: Processes a CSV file of complaints and writes the classification results to a new CSV file.
    input: input_file (Path to CSV), output_file (Path to CSV)
    output: Success message or Error log
    error_handling: Logs skipped rows if they are malformed or missing the description column.
