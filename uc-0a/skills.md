classify_complaint:
  name: classify_complaint
  description: Classifies a single complaint row into category, priority, reason, and flag based on description text
  input:
    type: dictionary
    format: complaint row with keys (complaint_id, description, and other metadata)
  output:
    type: dictionary
    format: classified row with keys (complaint_id, category, priority, reason, flag)
  error_handling: >
    If description is missing or empty, return category: Other, priority: Standard, 
    reason: "No description provided", flag: NEEDS_REVIEW. If category cannot be 
    determined from description, use category: Other and set flag: NEEDS_REVIEW.

batch_classify:
  name: batch_classify
  description: Reads input CSV, applies classify_complaint to each row, and writes output CSV with classifications
  input:
    type: string
    format: file path to input CSV with complaint data
  output:
    type: string
    format: file path to output CSV with columns (complaint_id, category, priority, reason, flag)
  error_handling: >
    If input file cannot be read, return error message. If individual rows fail 
    classification, continue processing other rows and include failed rows with 
    category: Other, flag: NEEDS_REVIEW. Always produce output file even if some rows fail.
