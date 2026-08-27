skills:
  - name: classify_complaint
    description: "Takes one complaint description as input and outputs a classified result including category, priority, reason, and flag."
    input: "String - The description of the citizen's complaint."
    output: "A dictionary with keys: category, priority, reason, flag."
    error_handling: "If the category is genuinely ambiguous, return 'NEEDS_REVIEW' in the flag. If no category matches, default to 'Other' and flag as 'NEEDS_REVIEW'."

  - name: batch_classify
    description: "Reads a list of complaints from a CSV file, applies the 'classify_complaint' skill to each, and writes the results to an output CSV file."
    input: "CSV File - contains 'description' column."
    output: "CSV File - contains 'category', 'priority', 'reason', 'flag' columns added/updated."
    error_handling: "Check for missing 'description' column. Log errors for rows that cannot be processed."
