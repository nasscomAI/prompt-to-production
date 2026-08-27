skills:
  - name: classify_complaint
    description: "Takes one complaint row and outputs category, priority, reason, and flag."
    input:
      type: object
      format: "Row containing 'complaint_id' and 'description'"
    output:
      type: object
      format: "Dictionary with 'complaint_id', 'category', 'priority', 'reason', and 'flag'"
    error_handling: "Return 'Other' category and flag 'NEEDS_REVIEW' on parsing failure or ambiguity."

  - name: batch_classify
    description: "Reads input CSV, applies classify_complaint per row, writes output CSV."
    input:
      type: object
      format: "Input and Output CSV file paths"
    output:
      type: null
      format: "Writes output to CSV"
    error_handling: "Flag nulls, do not crash on bad rows, produce output even if some rows fail."
