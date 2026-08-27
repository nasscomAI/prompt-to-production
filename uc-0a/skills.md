# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Classify one complaint row into a schema-compliant 4-field output
      (category, priority, reason, flag) without adding categories or guessing facts.
    input: >
      One complaint row as a dict with at least: complaint_id, description, ward,
      location, days_open. Rows may contain nulls in any field.
    output: >
      A dict with exactly five keys: complaint_id (preserved), category (one of:
      Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage,
      Heat Hazard, Drain Blockage, Other), priority (Urgent, Standard, or Low),
      reason (single sentence citing words from the description), flag
      (NEEDS_REVIEW or blank string).
    error_handling: >
      If the description is null, empty, or cannot be matched to any allowed
      category, output category "Other" with flag "NEEDS_REVIEW" rather than
      inventing a category. If a severity keyword is present, priority must be
      Urgent regardless of other signals.

  - name: batch_classify
    description: >
      Read the input CSV, apply classify_complaint to every row, and write the
      results CSV with the same complaint_id order as the input.
    input: >
      Input CSV path (test_[city].csv) and output CSV path (results_[city].csv).
      Input has a header row and one row per complaint.
    output: >
      A CSV written to output_path with a header row and columns: complaint_id,
      category, priority, reason, flag. One output row per input row.
    error_handling: >
      Never crash on a bad row: classify what can be classified, write
      category "Other", priority "Standard", and flag "NEEDS_REVIEW" for any row
      that fails, and always write a complete output file even if some rows fail.
      Nulls in non-essential fields are allowed.
