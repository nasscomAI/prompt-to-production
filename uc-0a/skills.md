# skills.md

skills:
  - name: classify_complaint
    description: Processes a single complaint description to determine its category, priority, and classification reasoning according to municipal rules.
    input: A single string representing the citizen's complaint description.
    output: An object containing category, priority, reason (citing description), and flag (NEEDS_REVIEW or blank).
    error_handling: If the category cannot be determined confidently from the description alone, set the category to 'Other' and the flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV file, applies the 'classify_complaint' skill to each row, and writes the results to a specified output CSV.
    input: Path to an input CSV file (test_[city].csv).
    output: Path to an output CSV file (results_[city].csv) with classified fields.
    error_handling: Logs rows that fail classification and continues processing the remainder of the file.
