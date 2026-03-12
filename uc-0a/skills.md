skills:

* name: classify_complaint
  description: Classifies a single citizen complaint description into category, priority, reason, and flag based on the defined taxonomy and urgency rules.
  input: A string containing the complaint description text.
  output: A structured object with fields: category (string), priority (string), reason (string), and flag (string or empty).
  error_handling: If the complaint description is missing, unclear, or cannot be confidently categorized, assign category "Other" and set flag to "NEEDS_REVIEW".

* name: batch_classify
  description: Processes a CSV file of complaint descriptions and applies classify_complaint to each row to produce a results CSV.
  input: A CSV file path containing complaint descriptions (e.g., test_pune.csv).
  output: A CSV file containing classification results with fields: category, priority, reason, and flag.
  error_handling: If the input CSV is missing required columns or contains invalid rows, skip those rows and mark them with category "Other" and flag "NEEDS_REVIEW".

