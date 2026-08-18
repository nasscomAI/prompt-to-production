# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen-complaint row into category, priority, reason, and flag.
    input: One complaint row as a dict — fields: complaint_id, date_raised, city, ward, location, description, reported_by, days_open.
    output: Dict with keys complaint_id, category, priority, reason, flag. category must be exactly one of "Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other" — exact strings only, no variations or sub-categories. priority must be "Urgent", "Standard", or "Low". reason is one sentence citing specific words from the description. flag is "NEEDS_REVIEW" or blank.
    error_handling: Priority becomes Urgent whenever the description contains a severity keyword (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse). If the description alone does not support a category, sets category to "Other" and flag to "NEEDS_REVIEW" instead of guessing.

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint to every row, and writes a complete results CSV.
    input: Path to a test_[city].csv with one complaint row per line; paths for input and output.
    output: Writes results_[city].csv with one output row per input row (complaint_id, category, priority, reason, flag).
    error_handling: Must not crash the run — flags a row as NEEDS_REVIEW or skips logging it while continuing, and always writes a complete results CSV even if some rows fail.
