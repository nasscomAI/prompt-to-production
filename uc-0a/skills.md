# skills.md

skills:
  - name: classify_complaint
    description: Receives one complaint row and classifies it into category, priority, reason, and flag.
    input: Dictionary containing complaint row details (specifically 'description').
    output: A dictionary with keys category, priority, reason, and flag adhering to strict allowed values.
    error_handling: Return category "Other", priority "Low", flag "NEEDS_REVIEW", and error reason if the input is malformed or completely empty.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint per row, and writes the results to an output CSV.
    input: String path to the input CSV and string path to the output CSV.
    output: None directly; writes a CSV file to the file system.
    error_handling: Skips completely empty rows but logs a warning and appends a default error result when encountering malformed rows without crashing.
