skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint description into a category, priority, reason, and ambiguity flag using the defined taxonomy.
    input: >
      A single complaint row as a plain-text string — the raw citizen-submitted
      description field. No category or priority data is provided.
    output: >
      A structured object with exactly four fields:
      category (one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage,
      Heritage Damage, Heat Hazard, Drain Blockage, Other);
      priority (one of: Urgent, Standard, Low);
      reason (one sentence citing specific words from the input description);
      flag (NEEDS_REVIEW or blank).
    error_handling: >
      If the description is empty or unparseable, return category: Other, priority: Low,
      reason: "Description missing or unreadable", and flag: NEEDS_REVIEW.
      If the description matches multiple categories (ambiguous), return the closest
      match for category and set flag: NEEDS_REVIEW — do not guess with false confidence.
      If a severity keyword (injury, child, school, hospital, ambulance, fire, hazard,
      fell, collapse) is present, always return priority: Urgent regardless of other signals.
      Never return a category string not in the allowed taxonomy — if no category fits,
      return Other with flag: NEEDS_REVIEW.

  - name: batch_classify
    description: Reads a city complaint CSV, applies classify_complaint to every row, and writes the fully classified output to a results CSV.
    input: >
      File path to a CSV file (test_[city].csv) containing 15 complaint rows with
      the category and priority_flag columns stripped. Each row must have at minimum
      a complaint_id and description field.
    output: >
      A CSV file written to uc-0a/results_[city].csv containing all original input
      columns plus four appended fields per row: category, priority, reason, and flag,
      populated for every row including those that triggered error handling.
    error_handling: >
      If an individual row is empty, malformed, or raises an exception during
      classification, write category: Other, priority: Low,
      reason: "Row processing error — could not classify", and flag: NEEDS_REVIEW
      for that row, log the row index and error to stderr, and continue processing
      all remaining rows without halting the batch.
      If the input file is not found, exit with a non-zero status and print a clear
      error message — do not produce a partial output file.
