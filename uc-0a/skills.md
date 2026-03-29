skills:
  - name: classify_complaint
    description: >
      Classify a single complaint row by category and priority while extracting a reason.
    input: >
      Dictionary containing a text description and other string properties.
    output: >
      Dictionary containing the assigned category, priority, extracted reason sentence, and flag.
    error_handling: >
      For ambiguous cases, categorize as Other and set flag to NEEDS_REVIEW; map category names to exact allowed strings only; assign Urgent priority if severity keywords found; specify a correct citing reason instead of a blank one.

  - name: batch_classify
    description: >
      Read input CSV, apply classification to each row individually, and write to output CSV.
    input: >
      String path for input CSV file and string path for output CSV file.
    output: >
      A CSV file containing all original rows populated with new prediction columns.
    error_handling: >
      Catch row-level errors so that a single bad row or null value does not crash the entire batch process.
