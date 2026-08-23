# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Accepts a single citizen complaint row and returns its category,
      priority, reason, and flag according to the municipal classification schema.
    input: A dictionary representing one CSV row with fields — complaint_id, date_raised,
      city, ward, location, description, reported_by, days_open.
    output: A dictionary with four fields — category (string, one of the 10 allowed
      values), priority (Urgent / Standard / Low), reason (one sentence citing words
      from the description), flag (NEEDS_REVIEW or empty string).
    error_handling: If the description field is empty or missing, set category to Other,
      priority to Low, reason to "No description provided", and flag to NEEDS_REVIEW.
      If the description is present but ambiguous across multiple categories, set flag
      to NEEDS_REVIEW and pick the closest matching category rather than returning an error.

  - name: batch_classify
    description: Reads an input CSV of citizen complaints, applies classify_complaint
      to every row, and writes the enriched results to an output CSV.
    input: Two file paths as strings — input_path pointing to the source CSV
      (with columns complaint_id, date_raised, city, ward, location, description,
      reported_by, days_open) and output_path for the results file.
    output: A CSV file written to output_path containing all original columns plus
      four new columns — category, priority, reason, flag — one row per complaint.
    error_handling: If the input file is not found, raise a FileNotFoundError with a
      clear message. If an individual row fails classification, write category as Other,
      priority as Low, and flag as NEEDS_REVIEW for that row and continue processing
      the remaining rows without stopping the batch.
