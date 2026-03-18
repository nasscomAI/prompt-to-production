# skills.md

skills:
  - name: classify_complaint
    description: Takes one complaint row in and returns category + priority + reason + flag out.
    input: Dictionary representing a single CSR row including the description.
    output: Dictionary with keys (complaint_id, category, priority, reason, flag).
    error_handling: Returns Category 'Other', Flag 'NEEDS_REVIEW' on ambiguity or failure.

  - name: batch_classify
    description: Reads input CSV, applies classify_complaint per row, writes output CSV.
    input: File paths for input CSV and output CSV.
    output: Writes parsed and classified rows to a new CSV file.
    error_handling: Logs rows that failed to process without crashing the batch job.
