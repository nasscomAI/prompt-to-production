# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into category, priority, reason, and flag based on the description.
    input: A single complaint row with description field (string).
    output: A dictionary/object with fields - category (string), priority (string), reason (string), flag (string or empty).
    error_handling: If input is invalid or description is missing, return category: Other, priority: Low, reason: "Invalid input", flag: NEEDS_REVIEW.

  - name: batch_classify
    description: Processes a CSV file of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: Input CSV file path (string) and output CSV file path (string).
    output: Writes a CSV file with additional columns for category, priority, reason, and flag.
    error_handling: If input file cannot be read or rows are malformed, skip invalid rows and log errors, but continue processing valid rows.
