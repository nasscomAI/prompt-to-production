# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag fields.
    input: "Dict with 'description' (str) field containing the citizen complaint text; may include additional fields like id, date, location"
    output: "Dict with 'category' (str, one of allowed values), 'priority' (str: Urgent/Standard/Low), 'reason' (str, single sentence citing description words), 'flag' (str: NEEDS_REVIEW or empty)"
    error_handling: "If description is empty or None, output category: Other, priority: Low, reason: No description provided, flag: NEEDS_REVIEW. If severity keywords are absent but category is ambiguous between two or more options, output the most likely category and set flag: NEEDS_REVIEW"

  - name: batch_classify
    description: Reads a CSV file of complaints, applies classify_complaint to each row, and writes results to an output CSV file.
    input: "Path to input CSV file with 'description' column; output path where results CSV will be written"
    output: "CSV file with columns: [original columns] + category, priority, reason, flag. Returns path to output file and count of successfully classified rows"
    error_handling: "If input file does not exist, raise FileNotFoundError. If CSV is malformed, output detailed error per row with category: Other, flag: NEEDS_REVIEW. If output directory does not exist, create it. Skip rows with empty descriptions and log them separately"
