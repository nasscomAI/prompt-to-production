# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint to determine its category, priority, reason, and flag based on the description provided.
    input: A single row or description string (text) representing a citizen complaint.
    output: A structured object (JSON) containing category (string), priority (string), reason (string), and flag (string/blank).
    error_handling: Sets category to 'Other' and sets the NEEDS_REVIEW flag if the description is genuinely ambiguous or lacks specific information for classification.

  - name: batch_classify
    description: Automates the process of reading an input CSV file of citizen complaints, applying classification to each row, and writing the results to an output CSV file.
    input: File path (string) to an input CSV file containing raw complaint descriptions.
    output: File path (string) to an output CSV file with classified categories, priority levels, reasons, and review flags.
    error_handling: Logs any malformed rows or data access issues to ensure that individual classification failures do not prevent the overall file from being processed.
