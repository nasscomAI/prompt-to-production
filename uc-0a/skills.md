# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into category, priority, reason, and flag based on the complaint description, ensuring taxonomic consistency and adherence to the classification schema.
    input: A dictionary representing a complaint row containing at least a 'description' field (string) with the complaint text.
    output: A dictionary with fields 'category' (exact string from allowed list), 'priority' (Urgent/Standard/Low), 'reason' (one sentence citing specific words from description), and 'flag' (NEEDS_REVIEW or blank).
    error_handling: If the category is genuinely ambiguous or cannot be determined from the description alone, sets flag to NEEDS_REVIEW and provides a reason explaining the ambiguity.

  - name: batch_classify
    description: Reads a CSV file of complaints, applies classify_complaint to each row, and writes the classified results to an output CSV file.
    input: Input CSV file path (string) and output CSV file path (string). The input CSV should have a 'description' column and lack 'category' and 'priority_flag' columns.
    output: Writes an output CSV file with the original columns plus 'category', 'priority', 'reason', and 'flag' columns for each row.
    error_handling: Handles file I/O errors by raising exceptions; delegates classification errors to classify_complaint, ensuring all rows are processed even if some are flagged for review.
