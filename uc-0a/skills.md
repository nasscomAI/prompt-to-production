# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into exact category, priority, one-sentence reason, and optional review flag.
    input: Dictionary representing a CSV row with fields complaint_id, date_raised, city, ward, location, description, reported_by, days_open.
    output: Dictionary with keys complaint_id, category, priority, reason, flag.
    error_handling: Validates category against allowed list of 10 categories. If ambiguous or non-matching, assigns category 'Other' and sets flag 'NEEDS_REVIEW'. If any severity keyword (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse) is found in description, assigns priority 'Urgent'. Always produces a one-sentence reason citing exact words from the description.

  - name: batch_classify
    description: Reads an input test CSV, applies classify_complaint to each row, and writes the output results CSV.
    input: File paths input_path (string) and output_path (string).
    output: CSV file created at output_path containing complaint_id, category, priority, reason, flag.
    error_handling: Handles null/missing fields gracefully, catches per-row errors without halting processing, and guarantees a compliant CSV output even with malformed input rows.
