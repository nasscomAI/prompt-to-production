# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category, priority, reason, and review flag using the fixed municipal taxonomy.
    input: >
      A dict representing one CSV row with keys complaint_id, date_raised, city,
      ward, location, description, reported_by, days_open. The description
      string is required for classification; other fields are optional context.
    output: >
      A dict with keys complaint_id (echoed from input), category (one of the
      ten allowed values), priority (Urgent, Standard, or Low), reason (one
      sentence citing words from description), flag (NEEDS_REVIEW or blank string).
    error_handling: >
      If description is missing or empty, return category Other, priority Low,
      reason stating that the description is missing or insufficient, and flag
      NEEDS_REVIEW. If description matches multiple allowed categories with
      equal plausibility (e.g. heritage street with lights out), pick the best
      fit only when one category is clearly dominant; otherwise return category
      Other with flag NEEDS_REVIEW. If severity keywords are present, always
      set priority to Urgent regardless of category ambiguity. Never raise an
      exception for a bad row — always return a complete output dict.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes a results CSV.
    input: >
      input_path (str): path to test_[city].csv with columns complaint_id,
      date_raised, city, ward, location, description, reported_by, days_open.
      output_path (str): path to write results CSV.
    output: >
      A CSV file at output_path with columns complaint_id, category, priority,
      reason, flag — one row per successfully processed input row, in input order.
    error_handling: >
      Flag rows with null or empty description in the output (category Other,
      flag NEEDS_REVIEW) rather than skipping them. If a single row fails
      classification logic, catch the error, write that row with category Other,
      priority Low, reason noting the processing failure, flag NEEDS_REVIEW, and
      continue processing remaining rows. Never crash the full batch because of
      one bad row. Produce the output file even when some rows need review.
      Validate that every written category is in the allowed list before saving.
