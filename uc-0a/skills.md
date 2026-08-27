# skills.md

skills:
  - name: classify_complaint
    description: One complaint row in, then category + priority + reason + flag out using the exact UC-0A schema.
    input: One complaint record as a dict containing at least a "description" key (string).
    output: A dict with four fields: category (one of the allowed category strings), priority (Urgent / Standard / Low), reason (one sentence citing words from description), flag (NEEDS_REVIEW or blank).
    error_handling: If the description is missing or empty, set category to Other, priority to Low, reason to "No description provided", and flag to NEEDS_REVIEW. If the category cannot be confidently determined, set category to Other and flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Reads input CSV, applies classify_complaint per row, and writes output CSV.
    input: Two string file paths — input_path (CSV with complaint rows including a description column) and output_path (destination for results).
    output: A CSV file at output_path containing all original columns plus category, priority, reason, and flag columns.
    error_handling: If the input file is not found or cannot be parsed, raise an error and halt. If an individual row fails classification, record category as Other, priority as Low, reason as "Classification error", flag as NEEDS_REVIEW, and continue processing remaining rows.
