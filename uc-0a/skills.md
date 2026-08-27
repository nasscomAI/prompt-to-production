# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Takes a single complaint description row and returns a structured classification with category, priority, reason, and flag.
    input: A plain-text complaint description string (one row from the input CSV).
    output: A CSV row with four fields — category (string, exact from allowed list), priority (Urgent/Standard/Low), reason (one sentence citing words from input), flag (NEEDS_REVIEW or blank).
    error_handling: If the category cannot be determined from the description alone, output category as "Other" and set flag to NEEDS_REVIEW. Never hallucinate a category or omit the reason field.

  - name: batch_classify
    description: Reads the full input CSV file, applies classify_complaint to each row, and writes the results to the output CSV.
    input: File path to a CSV with complaint description rows (category and priority_flag columns stripped).
    output: A CSV file at the specified output path with all original columns plus category, priority, reason, and flag populated for every row.
    error_handling: If a row has an empty or unreadable description, output category as "Other", priority as "Low", reason as "Description was empty or unreadable", and flag as NEEDS_REVIEW. Do not skip rows silently.
