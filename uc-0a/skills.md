# skills.md

skills:
  - name: classify_complaint
    description: Processes a single complaint description to determine its category, priority, reason, and review flag.
    input: A single dictionary representing a complaint row, containing the key 'description'.
    output: A dictionary containing the standard exact keys 'category', 'priority', 'reason', and 'flag'.
    error_handling: If the description is ambiguous, missing, or unreadable, the output returns category as 'Other' and sets flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Loads a dataset of complaints, applies classify_complaint to each row individually, and writes the output dataset.
    input: File paths mapped to the input CSV and the target output CSV.
    output: Writes a formatted CSV containing all input data alongside newly classified category, priority, reason, and flag columns.
    error_handling: Bypasses malformed rows safely, ensuring the pipeline never crashes on a bad row and successfully outputs all processable complaints.

