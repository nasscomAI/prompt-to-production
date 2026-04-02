# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category, priority, reason, and flag according to the predefined schema.
    input: A single complaint row object or dictionary containing at least a description field with the complaint text.
    output: A dictionary or object with four fields - category (exact string from allowed values), priority (Urgent/Standard/Low), reason (one sentence citing specific words), flag (NEEDS_REVIEW or blank).
    error_handling: If the complaint description is empty or invalid, return category as 'Other' and flag as 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV file, applies classify_complaint to each row, and writes the classified results to an output CSV file.
    input: File paths for input CSV (containing complaint descriptions) and output CSV.
    output: Writes a CSV file with additional columns for category, priority, reason, and flag for each input row.
    error_handling: If input file is missing or unreadable, raise an error; if output file cannot be written, raise an error; for individual row failures, mark as 'Other' with 'NEEDS_REVIEW' flag.
