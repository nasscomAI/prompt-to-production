skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag based on the description text.
    input: >
      A dictionary with keys: complaint_id (string), date_raised (string),
      city (string), ward (string), location (string), description (string),
      reported_by (string), days_open (int).
    output: >
      A dictionary with keys: complaint_id (string), category (string),
      priority (string), reason (string), flag (string — either NEEDS_REVIEW or empty).
    error_handling: >
      If description is missing, null, or empty, return category: Other,
      priority: Standard, reason: "Description missing", flag: NEEDS_REVIEW.
      If description is ambiguous with no clear category evidence, set
      category to Other and flag to NEEDS_REVIEW. Never raise an exception.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes results to an output CSV.
    input: >
      Two strings: input_path (path to CSV file with columns:
      complaint_id, date_raised, city, ward, location, description,
      reported_by, days_open) and output_path (path to write results CSV).
    output: >
      Writes a CSV file with columns: complaint_id, category, priority,
      reason, flag. Returns nothing (writes file as side effect).
    error_handling: >
      If a row cannot be parsed (malformed CSV, missing required fields),
      skip it and log a warning to stdout. Do not crash on bad rows.
      Produce output even if some rows fail. If input file does not exist,
      print an error message and exit with status code 1.
