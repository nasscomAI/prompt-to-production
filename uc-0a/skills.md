# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category, priority, reason, and flag using the fixed municipal taxonomy.
    input: A single complaint record with at least a `description` field (string).
    output: |
      A dict with four fields:
        category: one of [Pothole, Flooding, Streetlight, Waste, Noise, Road Damage,
                          Heritage Damage, Heat Hazard, Drain Blockage, Other]
        priority: one of [Urgent, Standard, Low]
        reason:   one sentence citing specific words from the description
        flag:     "NEEDS_REVIEW" if category is ambiguous, else blank string
    error_handling: >
      If description is missing or empty, return category: Other, priority: Low,
      reason: "No description provided", flag: NEEDS_REVIEW.
      If severity keywords are present but category is ambiguous, still set
      priority: Urgent and flag: NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV of complaint rows, applies classify_complaint to each row, and writes the results to an output CSV.
    input: >
      Path to input CSV file (string). CSV must contain a `description` column.
      Optional: --output path for the results file (defaults to results_<city>.csv).
    output: >
      A CSV file at the specified output path containing all original columns plus
      four new columns: category, priority, reason, flag. One row per input complaint.
    error_handling: >
      If the input file is not found or cannot be parsed, raise a clear error and
      exit without writing an output file. If an individual row fails classification,
      write category: Other, priority: Low, flag: NEEDS_REVIEW, and log the row
      index to stderr. Processing continues for remaining rows.
