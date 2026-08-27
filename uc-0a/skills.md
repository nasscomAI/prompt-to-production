skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint description into category, priority, reason, and review flag based on predefined schemas.
    input: A string containing the complaint description (e.g., "There's a big pothole on Main Street causing accidents").
    output: A JSON object with exactly four fields - category (string from allowed list), priority (Urgent/Standard/Low), reason (one sentence citing description words), flag (NEEDS_REVIEW or blank string).
    error_handling: If the description is ambiguous or category cannot be determined, sets category to "Other" and flag to "NEEDS_REVIEW"; otherwise, processes normally without errors.

  - name: batch_classify
    description: Reads a CSV file of complaints, applies classify_complaint to each row's description, and writes the results to an output CSV with added classification columns.
    input: Two file paths - input CSV path (containing at least a 'description' column) and output CSV path.
    output: Writes a new CSV file with original columns plus 'category', 'priority', 'reason', 'flag' columns for each row.
    error_handling: Skips rows with missing or invalid descriptions, logs warnings, and continues processing the rest; ensures output CSV is always created even if some rows fail.
