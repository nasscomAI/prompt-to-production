skills:
  - name: classify_complaint
    description: >
      Classify a single complaint row into an allowed category and urgency,
      producing a verifiable one-sentence reason grounded in the row's `description`.
    input: >
      One complaint row as a dict (from CSV) with at least:
      - complaint_id: string
      - description: string (free text)
    output: >
      A dict with keys:
      - complaint_id: string
      - category: one of Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
      - priority: Urgent or Standard
      - reason: one sentence string that quotes specific words/phrases from description
      - flag: either NEEDS_REVIEW or blank
    error_handling: >
      If `description` is missing/empty, return category Other, priority Standard,
      reason explaining that there is no evidence in description, and flag NEEDS_REVIEW.
      Never raise; always return a valid output dict.

  - name: batch_classify
    description: >
      Read the input city CSV, classify each row with classify_complaint, and write a
      results CSV in the required schema; continue even if some rows are problematic.
    input: >
      - input_path: string path to test_[city].csv
      - output_path: string path to write uc-0a/results_[city].csv
    output: >
      Writes a CSV with header:
      complaint_id, category, priority, reason, flag
    error_handling: >
      Uses csv.DictReader. For any row that fails validation/parsing, write a conservative
      Other + NEEDS_REVIEW result with a reason describing the failure mode, and continue processing.
