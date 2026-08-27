# skills.md — UC-0A Complaint Classifier

skills:

* name: classify_complaint
  description: Classifies one citizen complaint using the approved category, priority, reason, and review flag rules.
  input: A dictionary representing one complaint row containing a complaint ID and description.
  output: A dictionary containing complaint_id, category, priority, reason, and flag.
  error_handling: If the complaint is missing information or cannot be classified confidently, return category Other and flag NEEDS_REVIEW instead of guessing.

* name: batch_classify
  description: Reads complaints from an input CSV file, classifies each complaint, and writes the results to an output CSV file.
  input: The input CSV file path and output CSV file path.
  output: A CSV file containing complaint_id, category, priority, reason, and flag for every complaint.
  error_handling: Invalid or incomplete rows must not crash the batch; flag problematic rows as NEEDS_REVIEW and continue processing the remaining complaints.
