skills:
  - name: classify_complaint
    description: Classifies one complaint row into schema-locked category, priority, reason, and ambiguity flag using only complaint text.
    input: A single complaint record object with text fields from one CSV row (for example complaint_id/title/description), where description text is required.
    output: A record with category (one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other), priority (Urgent|Standard|Low), reason (one sentence citing words from the complaint), and flag (NEEDS_REVIEW or blank).
    error_handling: If description text is missing or empty, return category=Other, priority=Standard, reason="Insufficient complaint text for classification.", and flag=NEEDS_REVIEW. If category is ambiguous from text, return category=Other and flag=NEEDS_REVIEW instead of guessing.

  - name: batch_classify
    description: Reads the input complaints CSV, applies classify_complaint row-by-row, and writes results_[city].csv with required UC-0A columns.
    input: Input CSV path containing complaint rows where category and priority_flag are absent, and output CSV path for results.
    output: Output CSV with one result row per input row including category, priority, reason, and flag; priority is set to Urgent when severity keywords appear (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse).
    error_handling: If required CSV inputs are missing, malformed, or unreadable, fail with explicit error and no partial silent success. For ambiguous rows, write category=Other and flag=NEEDS_REVIEW while preserving row count.
