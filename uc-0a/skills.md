# skills.md

skills:
  - name: "classify_complaint"
    description: "Evaluates a single complaint row based on RICE enforcement rules and returns a structured classification including category, priority, reason, and flag."
    input: "Dictionary representing a CSV row with keys like 'description' and 'complaint_id'."
    output: "Dictionary with keys: 'complaint_id', 'category', 'priority', 'reason', and 'flag'."
    error_handling: "Returns category 'Other' and flag 'NEEDS_REVIEW' if description is missing, empty, or genuinely ambiguous."

  - name: "batch_classify"
    description: "Reads a municipal complaint CSV, applies classification logic to each row, and saves the results to an output CSV file."
    input: "Paths to the input CSV file and the desired output CSV file."
    output: "Success message indicating results have been written to the output file."
    error_handling: "Uses try-except blocks to catch CSV parsing errors and ensures every input row is represented in the output file even if individual row processing fails."
