# skills.md — UC-0A Complaint Classifier

skills:
  - name: "classify_complaint"
    description: "Takes one complaint row and produces category, priority, reason, and flag."
    input: "Object (with description: string)."
    output: "Object (category: string, priority: string, reason: string, flag: string)."
    error_handling: "If the category is genuinely ambiguous or the description is non-sensical, set category to 'Other' and flag to 'NEEDS_REVIEW'."

  - name: "batch_classify"
    description: "Reads input CSV, applies classify_complaint per row, and writes to an output CSV."
    input: "String (path to input CSV file)."
    output: "String (path to output CSV file)."
    error_handling: "If the input file path is invalid or the CSV structure is missing required columns, stop processing and return an error message."
