# skills.md


skills:
  - name: "classify_complaint"
    description: "Transforms a single citizen complaint description into a structured classification (category, priority, reason, flag)."
    input: "Citizen complaint string (text description)."
    output: "JSON object containing 'category', 'priority', 'reason', and 'flag'."
    error_handling: "If description is ambiguous or unintelligible, set category to 'Other' and flag to 'NEEDS_REVIEW'."

  - name: "batch_classify"
    description: "Orchestrates the classification of multiple complaints by reading from an input CSV and writing results to an output CSV."
    input: "Input CSV file path (containing 'description')."
    output: "Output CSV file path (containing classifications)."
    error_handling: "Logs file errors and ensures the process completes even if individual rows trigger 'NEEDS_REVIEW'."
