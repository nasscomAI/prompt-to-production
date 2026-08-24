# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Classifies a single citizen complaint description into a category, priority,
      reason, and flag, applying the UC-0A classification schema exactly.
    input: >
      A single complaint row — the description text as a string extracted from the
      input CSV.
    output: >
      A dict with four fields: category (exactly one of Pothole, Flooding, Streetlight,
      Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other),
      priority (Urgent | Standard | Low), reason (a one-sentence justification citing
      specific words from the description), flag (NEEDS_REVIEW or blank).
    error_handling: >
      If the category cannot be determined from the description alone, outputs
      category: Other and flag: NEEDS_REVIEW instead of guessing. Priority is Urgent
      whenever a severity keyword (injury, child, school, hospital, ambulance, fire,
      hazard, fell, collapse) appears. Never invents categories or variations of the
      allowed list.

  - name: batch_classify
    description: >
      Reads the city test CSV, applies classify_complaint to every row, and writes the
      results CSV with the classification columns appended.
    input: >
      Path to ../data/city-test-files/test_[city].csv — 15 complaint rows; the category
      and priority_flag columns are stripped.
    output: >
      Writes uc-0a/results_[city].csv with all original columns plus category, priority,
      reason, and flag for every row.
    error_handling: >
      Validates that the required columns exist and every row is processed. Ambiguous
      rows keep category: Other and flag: NEEDS_REVIEW — never guessed. No rows are
      dropped or merged.
