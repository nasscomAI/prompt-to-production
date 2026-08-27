# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into a category, priority, reason, and optional review flag using the CMC taxonomy.
    input: A dict representing one CSV row with columns — complaint_id, date_raised, city, ward, location, description, reported_by, days_open. Only the description field is used for classification.
    output: A dict with keys — complaint_id, category (exact string from allowed list), priority (Urgent/Standard/Low), reason (one sentence citing specific words from the description), flag (NEEDS_REVIEW or blank).
    error_handling: If description is missing or empty, set category to Other, priority to Low, reason to 'Description missing — cannot classify', and flag to NEEDS_REVIEW. Never invent a category outside the allowed list. Never use ward, location, city, or days_open to infer or adjust the classification.

  - name: batch_classify
    description: Reads an input CSV of complaint rows, applies classify_complaint to each row, and writes the results to an output CSV.
    input: input_path (str) pointing to a city test CSV (columns: complaint_id, date_raised, city, ward, location, description, reported_by, days_open), output_path (str) for the results file.
    output: A CSV file at output_path with columns — complaint_id, category, priority, reason, flag — one row per input complaint.
    error_handling: If an individual row fails classification, write category Other, priority Low, reason 'Row processing error', flag NEEDS_REVIEW for that row and continue — do not halt the entire batch.
