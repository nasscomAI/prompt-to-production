skills:
  - name: classifying_complaint
    description: Takes a single complaint row and classifies it into a category and priority.
    input: Dictionary representing a single complaint row.
    output: Dictionary with keys complaint_id, category, priority, reason, flag.
    error_handling: Returns a dictionary with flag set to ERROR and reason populated if input is invalid.

  - name: batch_processing
    description: Reads an input CSV, classifies each row using classifying_complaint, and writes results to an output CSV.
    input: File paths to input CSV and output CSV as strings.
    output: Generates a CSV file containing the classification results.
    error_handling: Flags null rows, logs errors, and skips bad rows to ensure complete processing of valid rows without crashing.
