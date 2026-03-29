# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint to determine its category, priority, and justification.
    input: String containing a citizen complaint description.
    output: A structured object {category: string, priority: string, reason: string, flag: string}.
    error_handling: "If input is empty or ambiguous, returns category: Other + flag: NEEDS_REVIEW."

  - name: batch_classify
    description: Processes an input file containing multiple citizen complaints and outputs the results to a CSV.
    input: Path to an input CSV file containing citizen descriptions.
    output: Path to an output CSV file with the classifications.
    error_handling: "If a row fails to process, logs the error and continues with the next row in the batch."
