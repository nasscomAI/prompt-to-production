# skills.md
skills:
  - name: classify_complaint
    description: >
      Classifies a single citizen complaint description into the required
      municipal category and priority while generating a justification.
    input: >
      A single complaint description string from the CSV row.
    output: >
      A structured result containing:
      category (one of the allowed taxonomy values),
      priority (Urgent, Standard, or Low),
      reason (one sentence citing words from the complaint),
      flag (NEEDS_REVIEW or blank).
    error_handling: >
      If the complaint description is empty or the category cannot be
      confidently determined, return category as "Other" and set flag
      to NEEDS_REVIEW.

  - name: batch_classify
    description: >
      Processes an entire complaints CSV file by applying classify_complaint
      to every row and writing the structured results to an output CSV file.
    input: >
      Input CSV file path containing complaint descriptions
      (e.g., ../data/city-test-files/test_hyderabad.csv).
    output: >
      Output CSV file containing the original complaint description along with
      category, priority, reason, and flag columns.
    error_handling: >
      If the input file cannot be read or contains invalid rows, skip the
      problematic row, log the issue, and continue processing remaining rows.