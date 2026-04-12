# skills.md

skills:
  - name: classify_complaint
    description: Classifies a citizen complaint description into category, priority, reason, and flag.
    input: "description: string"
    output: '{"category": "string", "priority": "string", "reason": "string", "flag": "string"}'
    error_handling: "If ambiguous, use Other and NEEDS_REVIEW flag."

  - name: batch_classify
    description: Reads input CSV, applies classify_complaint per row, writes output CSV.
    input: "input_csv_path: string, output_csv_path: string"
    output: "boolean success"
    error_handling: "Process as many rows as possible, log errors for failed rows."
