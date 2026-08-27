skills:
  - name: classify_complaint
    description: "Classifies a single citizen complaint row into category, priority, reason, and review flag based on its description text."
    input: "A dictionary representing a single CSV row, including keys for 'complaint_id' (string) and 'description' (string)."
    output: "A dictionary with keys 'complaint_id' (string), 'category' (string), 'priority' (string), 'reason' (string), and 'flag' (string)."
    error_handling: "If 'description' is missing, empty, or null, sets category to 'Other', priority to 'Standard', reason to a descriptive error message, and flag to 'NEEDS_REVIEW'. If the complaint description is genuinely ambiguous, sets category to 'Other' and flag to 'NEEDS_REVIEW'."

  - name: batch_classify
    description: "Reads citizen complaints from an input CSV file, processes each complaint row using the classify_complaint skill, and writes the results to an output CSV file."
    input: "An input file path (string) to a CSV file and an output file path (string) to write the results."
    output: "Creates or overwrites a CSV file at the output path containing columns: complaint_id, category, priority, reason, and flag."
    error_handling: "If the input CSV file cannot be read, does not exist, or is empty, raises an appropriate exception or logs the failure and aborts. If processing of an individual row fails or raises an error, logs the row error, flags the row with category 'Other' and flag 'NEEDS_REVIEW', and proceeds to process the next row to ensure execution does not crash."
