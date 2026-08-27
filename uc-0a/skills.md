skills:
  - name: classify_complaint
    description: Takes a single complaint row and returns a classification with category, priority, reason, and an optional review flag.
    input: A single row of complaint data as a string or dict, containing at minimum a description field.
    output: A dict with four fields — category (string from allowed list), priority (Urgent/Standard/Low), reason (one sentence referencing complaint text), flag (NEEDS_REVIEW or blank).
    error_handling: If the description field is empty or missing, return category as 'Other', priority as 'Low', reason as 'No description provided', and flag as 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV file, applies classify_complaint to every row, and writes the results to an output CSV file.
    input: Two file paths as strings — input CSV path and output CSV path.
    output: A CSV file at the output path containing all original columns plus the four new fields — category, priority, reason, flag.
    error_handling: If the input file is not found, stop and print a clear error message with the file path. If a row fails classification, write 'ERROR' in the category field and 'NEEDS_REVIEW' in the flag field for that row, then continue processing remaining rows.