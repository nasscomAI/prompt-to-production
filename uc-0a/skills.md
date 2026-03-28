skills:
  - name: classify_complaint
    description: Classify a single complaint row into category, priority, reason, and flag using UC-0A schema rules.
    input:
      type: object
      format: "{ 'description': 'string', ... }"
    output:
      type: object
      format: "{ 'category': 'Pothole|Flooding|Streetlight|Waste|Noise|Road Damage|Heritage Damage|Heat Hazard|Drain Blockage|Other', 'priority': 'Urgent|Standard|Low', 'reason': 'string', 'flag': 'NEEDS_REVIEW|'}"
    error_handling: "If description missing or invalid, raise validation error; if ambiguous, set category to Other and flag to NEEDS_REVIEW; enforce exact category list and severity keyword to Urgent mapping."

  - name: batch_classify
    description: Read input CSV, apply classify_complaint for each row, and write output CSV with validated results.
    input:
      type: object
      format: "{ 'input_path': '../data/city-test-files/test_[your-city].csv', 'output_path': 'uc-0a/results_[your-city].csv' }"
    output:
      type: object
      format: "{ 'rows_processed': integer, 'output_path': 'string', 'errors': [ ... ] }"
    error_handling: "If input_path missing or non-existent, raise error; for invalid rows, log error and continue with flag NEEDS_REVIEW or category Other; ensure no invalid category values are emitted and reason is always present."

