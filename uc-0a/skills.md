skills:

  - name: classify_complaint
    description: >
      Classifies a single citizen complaint row into one CMC category with a
      priority, a one-sentence cited reason, and an ambiguity flag.
    input: >
      One complaint row (dict) with at least a description field and a
      complaint_id.
    output: >
      A dict with keys: complaint_id, category, priority, reason, flag.
      category is exactly one of the allowed 10 values; priority is Urgent or
      Standard; flag is NEEDS_REVIEW or blank.
    error_handling: >
      Empty/missing description: returns category Other, priority Standard,
      reason explains that the description is empty, flag NEEDS_REVIEW.
      Genuinely ambiguous description (conflicting category signals, safety
      hazard, or no taxonomy match): returns the best-fit category with
      flag NEEDS_REVIEW rather than guessing.

  - name: batch_classify
    description: >
      Reads an input CSV of complaints, applies classify_complaint to every
      row, and writes the results CSV with parsed-out classification columns.
    input: >
      Input CSV path (e.g. ../data/city-test-files/test_pune.csv) and an output
      CSV path (e.g. results_pune.csv).
    output: >
      A CSV written to the output path with columns:
      complaint_id, category, priority, reason, flag.
    error_handling: >
      Never crashes the whole batch on a bad row; a failed row is written as
      category Other, flag NEEDS_REVIEW. Null fields are tolerated. The output
      file is always produced even if some rows fail.