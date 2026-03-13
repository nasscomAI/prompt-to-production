# skills.md — UC-0A Complaint Classifier Skills

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into a category with priority, reason, and review flag.
    input: >
      A single complaint record (dict or CSV row) with fields: complaint_id,
      date_raised, city, ward, location, description, reported_by, days_open.
    output: >
      A dict with four fields:
      category (exactly one of: Pothole, Flooding, Streetlight, Waste, Noise,
      Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other),
      priority (exactly one of: Urgent, Standard, Low),
      reason (one sentence citing specific words from the description),
      flag (NEEDS_REVIEW if category is genuinely ambiguous, blank otherwise).
    error_handling: >
      If the description is empty, null, or too short to classify, set
      category to Other, priority to Standard, and flag to NEEDS_REVIEW.
      If severity keywords (injury, child, school, hospital, ambulance,
      fire, hazard, fell, collapse) are present, priority must be Urgent
      regardless of other factors.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes a classified output CSV.
    input: >
      A file path (string) to a CSV containing complaint records with columns:
      complaint_id, date_raised, city, ward, location, description,
      reported_by, days_open.
    output: >
      A CSV file where each row contains all original fields plus four new
      columns: category, priority, reason, and flag.
    error_handling: >
      If a row is malformed or has missing required fields, skip the row,
      log it to stderr, and continue processing the remaining rows.
      Return a non-zero exit code if any rows were skipped.
