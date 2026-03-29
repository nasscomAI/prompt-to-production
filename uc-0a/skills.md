# skills.md

skills:
  - name: classify_complaint
    description: Classifies one complaint description into UC-0A category, priority, reason, and flag using only the allowed schema.
    input: One complaint row as text (description field from CSV).
    output: >
      Structured record with fields:
      category (Pothole|Flooding|Streetlight|Waste|Noise|Road Damage|Heritage Damage|Heat Hazard|Drain Blockage|Other),
      priority (Urgent|Standard|Low),
      reason (one sentence citing words from description),
      flag (NEEDS_REVIEW or blank).
    error_handling: >
      If description is empty or unusable, return category=Other, priority=Standard,
      reason explaining missing evidence, and flag=NEEDS_REVIEW.
      If classification is genuinely ambiguous, set category=Other and flag=NEEDS_REVIEW.

  - name: batch_classify
    description: Reads a UC-0A input CSV, applies classify_complaint to each row, and writes output CSV with required fields.
    input: CSV file path containing complaint rows with stripped category and priority_flag columns.
    output: CSV file where each row contains category, priority, reason, and flag populated per UC-0A schema.
    error_handling: >
      For malformed rows, still emit a row with category=Other and flag=NEEDS_REVIEW,
      plus a reason that references the parsing issue; do not invent categories.
