skills:
  - name: classify_complaint
    description: Classifies one complaint row into constrained category, priority, reason, and ambiguity flag.
    input: >
      One complaint row as a dictionary/object with at least a `description` string
      (other row-local fields may be present and can be used only as supporting context).
    output: >
      A dictionary/object with keys: `category`, `priority`, `reason`, `flag`.
      `category` must be one of: Pothole, Flooding, Streetlight, Waste, Noise,
      Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other.
      `priority` must be one of: Urgent, Standard, Low.
      `reason` must be one sentence citing words from the description.
      `flag` must be `NEEDS_REVIEW` or blank.
    error_handling: >
      If description is missing/empty, return `category: Other`, `priority: Standard`,
      a reason stating insufficient description evidence, and `flag: NEEDS_REVIEW`.
      If category evidence is genuinely ambiguous, return `category: Other` and `flag: NEEDS_REVIEW`.
      If severity keywords appear (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse),
      force `priority: Urgent`.

  - name: batch_classify
    description: Reads an input complaints CSV, applies classify_complaint row-by-row, and writes the output CSV.
    input: >
      `input_csv_path` and `output_csv_path` strings, where input contains complaint rows
      (with category/priority labels removed for evaluation).
    output: >
      Output CSV at `output_csv_path` containing each original row plus standardized
      classification fields `category`, `priority`, `reason`, and `flag` for all rows.
    error_handling: >
      Validate file readability/writability and required `description` column before processing.
      On row-level ambiguity or invalid description, still emit a row using fallback:
      `category: Other`, evidence-based reason, and `flag: NEEDS_REVIEW`.
      Never emit non-schema labels.
