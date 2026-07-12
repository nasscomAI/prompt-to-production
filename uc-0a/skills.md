skills:
  - name: classify_complaint
    description: >
      Classifies a single civic complaint row into a category, priority level,
      reason, and review flag based solely on the description field.
    input: >
      A dictionary representing one CSV row with keys: complaint_id (string),
      date_raised (string, YYYY-MM-DD), city (string), ward (string),
      location (string), description (string), reported_by (string),
      days_open (integer).
    output: >
      A dictionary with keys: complaint_id (string, carried from input),
      category (string, one of: Pothole, Flooding, Streetlight, Waste, Noise,
      Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other),
      priority (string, one of: Urgent, Standard, Low), reason (string,
      one sentence citing description words), flag (string, NEEDS_REVIEW or empty).
    error_handling: >
      If the description field is missing or empty, return category: Other,
      priority: Low, reason: "No description provided", flag: NEEDS_REVIEW.
      If the complaint_id is missing, raise a ValueError.

  - name: batch_classify
    description: >
      Reads an input CSV of civic complaints, applies classify_complaint to
      each row, and writes the classified results to an output CSV.
    input: >
      input_path (string): filesystem path to a CSV file with columns
      complaint_id, date_raised, city, ward, location, description,
      reported_by, days_open. output_path (string): filesystem path for
      the output CSV.
    output: >
      A CSV file written to output_path with columns: complaint_id, category,
      priority, reason, flag. One row per input row, preserving original order.
    error_handling: >
      If a row cannot be classified (e.g. malformed or missing required fields),
      write that row with category: Other, priority: Low, reason:
      "Row processing error", flag: NEEDS_REVIEW. Never skip rows or crash.
      If the input file does not exist, raise FileNotFoundError with a clear
      message. If the output directory does not exist, raise FileNotFoundError.
