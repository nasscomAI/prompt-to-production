# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint row and determines its standardized category, priority, parsing flag, and reasoning.
    input: A single dictionary or JSON object representing a row, typically containing a 'description' or 'complaint' text field.
    output: A dictionary with the exact keys - category, priority, reason, and flag.
    error_handling: If the input is missing, empty, or completely ambiguous, return category "Other", flag "NEEDS_REVIEW", and state the issue in the reason field.

  - name: batch_classify
    description: Reads an input CSV file of multiple complaints, iterates over each to classify it, and writes the classified records to an output CSV file.
    input: Two strings representing the file paths for the input CSV and the output CSV.
    output: A newly created output CSV file containing all processed rows, including flagged ones.
    error_handling: Gracefully handles nulls and malformed rows by flagging them (e.g., flag: "NEEDS_REVIEW"), and ensures the batch process continues without crashing.
