# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag based on the description.
    input: A dictionary representing a complaint row, containing at least the 'description' field as a string.
    output: A dictionary with keys: category (string), priority (string), reason (string), flag (string or blank).
    error_handling: If description is missing, empty, or invalid, set category to 'Other' and flag to 'NEEDS_REVIEW'; continue processing without crashing.

  - name: batch_classify
    description: Reads a CSV file of complaints, applies classify_complaint to each row, and writes the classified results to a new CSV file.
    input: Input file path (string) to the CSV file and output file path (string) for the results CSV.
    output: None (writes to the output file); prints a completion message to console.
    error_handling: Skips rows with invalid data, flags them appropriately, ensures the output file is produced even if some rows fail; does not crash on bad input rows.
