# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into category and priority level based on description text.
    input: "String (complaint description)"
    output: "Object with fields: category (string), priority (string: Urgent/Standard/Low), reason (string), flag (string: NEEDS_REVIEW or blank)"
    error_handling: "If description is empty or null, return category=Other, priority=Standard, reason='No description provided', flag=NEEDS_REVIEW"

  - name: batch_classify
    description: Reads CSV file of complaints and classifies each row using classify_complaint skill, writing results to output CSV.
    input: "File path to input CSV (columns: id, category, priority, description; category and priority may be stripped) and output file path"
    output: "CSV file (columns: id, category, priority, reason, flag) in same row order as input"
    error_handling: "If row has missing description, output category=Other, priority=Standard, reason='No description provided', flag=NEEDS_REVIEW. If file malformed, log error to stderr with row number and skip row. Continue processing remaining rows."
