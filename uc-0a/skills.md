# skills.md

skills:
  - name: classify_complaint
    description: Classify a single complaint row into a standardized category, priority, reason and flag based on RICE enforcement rules.
    input: A string description of the civic complaint.
    output: A dictionary containing: category (string), priority (string), reason (string), flag (string).
    error_handling: Return category as Other and flag as NEEDS_REVIEW if ambiguous or input is malformed.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the output to a new CSV file.
    input: input_path (string) for the source CSV and output_path (string) for the destination CSV.
    output: None (Writes a CSV file as a side-effect).
    error_handling: Skip malformed rows, log warning, but do not crash. Write results even if some rows fail.
