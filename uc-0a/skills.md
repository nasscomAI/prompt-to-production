# skills.md

skills:
  - name: classify_complaint
    description: Classifies one complaint into category, priority, reason, and flag.
    input: One complaint row as dictionary input.
    output: Dictionary containing complaint_id, category, priority, reason, and flag.
    error_handling: Returns category as Other and flag as NEEDS_REVIEW if complaint is ambiguous.

  - name: batch_classify
    description: Reads input CSV, classifies all complaints, and writes output CSV.
    input: Input CSV file path and output CSV file path.
    output: CSV file with classified complaint results.
    error_handling: Skips invalid rows safely without crashing the program.