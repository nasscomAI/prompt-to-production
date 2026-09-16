# skills.md

skills:
  - name: classify_complaint
    description: Classifies one citizen complaint row into the UC-0A category, priority, reason, and review flag schema.
    input: >
      A dictionary representing one CSV row. Expected fields include
      complaint_id and a complaint description field. Missing optional fields
      must not prevent classification.
    output: >
      A dictionary with exactly these classification fields:
      complaint_id, category, priority, reason, and flag. Category must be one
      of Pothole, Flooding, Streetlight, Waste, Noise, Road Damage,
      Heritage Damage, Heat Hazard, Drain Blockage, or Other. Priority must be
      Urgent, Standard, or Low. Flag must be NEEDS_REVIEW or blank.
    error_handling: >
      If the description is missing, blank, malformed, or too ambiguous to map
      to one allowed category, return category Other, flag NEEDS_REVIEW, and a
      reason explaining the unsupported or ambiguous input. If any severity
      keyword is present, set priority to Urgent even when category is Other.

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint to each row, and writes a UC-0A results CSV.
    input: >
      An input CSV path containing complaint rows and an output CSV path where
      results should be written.
    output: >
      A CSV file containing one output row per input row with columns
      complaint_id, category, priority, reason, and flag.
    error_handling: >
      The batch process must not crash because of a bad row. It must preserve
      row count by writing a result for every input row. Rows that cannot be
      safely interpreted must be written as category Other with flag
      NEEDS_REVIEW and an explanatory reason.
