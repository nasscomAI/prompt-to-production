# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint description into a category, priority level, reason, and optional review flag.
    input: One complaint row dict with a 'description' key containing plain text of the citizen complaint.
    output: A structured dict with four fields — category (exact taxonomy string), priority (Urgent / Standard / Low), reason (one sentence citing words from the description), and flag (NEEDS_REVIEW or blank).
    error_handling: If the description is empty or missing, return category: Other, priority: Low, flag: NEEDS_REVIEW, and a reason stating the description was insufficient — never raise an unhandled error.

  - name: batch_classify
    description: Reads an input CSV of complaint rows, applies classify_complaint to every row, and writes the fully classified results to an output CSV.
    input: File path to a CSV containing at least a 'description' column (15 rows per city; category and priority_flag columns are stripped in test files).
    output: A CSV file at the specified output path with all original columns plus category, priority, reason, and flag appended for every row.
    error_handling: If a row is malformed or the description field is missing, write category: Other, priority: Low, flag: NEEDS_REVIEW, and a descriptive reason — then continue processing all remaining rows without halting.
