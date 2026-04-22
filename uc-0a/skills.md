# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint to determine its municipal category and priority.
    input: A dictionary representing a single row from the complaint CSV (e.g., {'description': '...', 'location': '...'}).
    output: A dictionary containing category (string), priority (string), reason (string), and flag (string).
    error_handling: If description is missing, set category to 'Other' and flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Orchestrates the classification of multiple complaints from an input CSV file and saves the results.
    input: Paths for the input CSV file and the target output CSV file.
    output: A status message confirming the number of rows processed and the output file path.
    error_handling: If input file is not found, raise a FileNotFoundError and log the error.
