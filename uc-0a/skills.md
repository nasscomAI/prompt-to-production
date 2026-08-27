skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint description into a category and priority, with a cited reason and an optional ambiguity flag.
    input:
      type: object
      fields:
        - complaint_id: string — unique identifier for the complaint row
        - description: string — raw citizen complaint text
    output:
      type: object
      fields:
        - complaint_id: string — echoed from input for traceability
        - category: string — exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
        - priority: string — exactly one of: Urgent, Standard, Low
        - reason: string — one sentence citing specific words from the description that justify the classification
        - flag: string — "NEEDS_REVIEW" if category is genuinely ambiguous, otherwise blank
    error_handling:
      - If description is empty or too short to classify, output category as "Other", priority as "Low", and flag as "NEEDS_REVIEW".
      - If a severity keyword (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse) is detected, priority MUST be set to "Urgent" regardless of other signals.
      - Never invent or abbreviate category names — non-matching input maps to "Other".

  - name: batch_classify
    description: Reads a CSV of citizen complaints, applies classify_complaint to each row, and writes a classified output CSV.
    input:
      type: file (CSV)
      format: Rows with columns complaint_id and description; category and priority columns are absent or stripped.
      example_path: ../data/city-test-files/test_[your-city].csv
    output:
      type: file (CSV)
      format: Same rows with four appended columns — category, priority, reason, flag — for every input row.
      example_path: uc-0a/results_[your-city].csv
    error_handling:
      - Rows with missing or blank description are classified as Other / Low / NEEDS_REVIEW and written to output with a reason of "Description was empty or missing."
      - Malformed CSV rows are skipped and logged to stderr with the row index.
      - The output file is always written even if some rows fail; failed rows appear with flag set to "NEEDS_REVIEW".
