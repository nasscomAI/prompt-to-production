# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint record into category, priority, reason, and flag.
    input: A dictionary with keys: id, description (string containing the citizen complaint text).
    output: A dictionary with keys: id, category, priority, reason, flag.
    error_handling: If description is empty or unreadable, output category: Other, priority: Low, reason: "Unable to classify — empty description", flag: NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: File path to input CSV (must contain id and description columns).
    output: File path to output CSV with columns: id, category, priority, reason, flag.
    error_handling: If input file is missing or malformed, raise an error with a clear message. If individual rows fail classification, process remaining rows and log failures with NEEDS_REVIEW flag.
