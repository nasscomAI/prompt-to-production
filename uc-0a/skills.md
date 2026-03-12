# skills.md

skills:
  - name: classify_complaint
    description: Receives one complaint row and determines its exact category, priority severity, explicit reasoning, and ambiguity flag.
    input: "One complaint row containing at least a description field (string)."
    output: "Returns category (string), priority (string), reason (string), and flag (string)."
    error_handling: "If input is invalid, ambiguous, or lacks detail, flag it as NEEDS_REVIEW and categorize as Other."

  - name: batch_classify
    description: Reads an input CSV containing multiple complaints, applies classification per row, and writes to an output CSV.
    input: "input_path (string): path to input csv, output_path (string): path to write results."
    output: "A CSV file saved at output_path containing classified details for each row."
    error_handling: "Do not crash on bad rows; write them with processing error as reason. Create file even if some rows fail."
