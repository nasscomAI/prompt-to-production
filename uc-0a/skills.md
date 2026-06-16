# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint description into category, priority, reason, and flag according to the fixed taxonomy and enforcement rules in agents.md.
    input: >
      A single complaint record as a dict with at minimum a `description` field (string).
      Example: {"id": "001", "description": "Large pothole near school gate, child fell"}
    output: >
      A dict with exactly four fields:
        category  — one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage,
                    Heritage Damage, Heat Hazard, Drain Blockage, Other
        priority  — one of: Urgent, Standard, Low
        reason    — one sentence quoting specific words from the input description
        flag      — "NEEDS_REVIEW" if category is genuinely ambiguous, otherwise blank
      Example: {"category": "Pothole", "priority": "Urgent", "reason": "Description mentions 'school gate' and 'child fell', triggering Urgent severity.", "flag": ""}
    error_handling: >
      If `description` is missing or empty, return category: Other, priority: Low,
      reason: "No description provided — cannot classify.", flag: NEEDS_REVIEW.
      Never invent a category; if ambiguous, always output Other + NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV of complaint rows, applies classify_complaint to each row, and writes the results to an output CSV.
    input: >
      Two file paths (strings):
        input_path  — path to the source CSV (must contain a `description` column)
        output_path — path where the result CSV will be written
      Example: input_path="../data/city-test-files/test_pune.csv", output_path="results_pune.csv"
    output: >
      A CSV file at output_path containing all original columns plus four appended columns:
        category, priority, reason, flag
      Also returns a summary dict: {"total": N, "urgent": N, "needs_review": N, "errors": N}
    error_handling: >
      If the input file is missing or the `description` column is absent, abort with a
      clear error message and do not create an output file.
      If an individual row fails classification, write category: Other, flag: NEEDS_REVIEW,
      and reason: "Row classification error: <error detail>" for that row and continue
      processing remaining rows — never crash the batch on a single bad row.
