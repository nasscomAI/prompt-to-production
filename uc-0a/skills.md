# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single civic complaint into a specific category and determines its priority level based on text analysis.
    input: A single complaint description string.
    output: A structured object containing: category (string), priority (Urgent/Standard/Low), reason (one sentence), and flag (NEEDS_REVIEW or blank).
    error_handling: If the description is empty or completely unintelligible, assign category 'Other', priority 'Low', and set flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Orchestrates the classification process for an entire dataset provided in CSV format.
    input: An input CSV file path containing citizen complaints.
    output: An output CSV file path containing the original data plus the four classification fields.
    error_handling: Validates the presence of required columns; if the 'description' column is missing, the process logs an error and halts execution.
