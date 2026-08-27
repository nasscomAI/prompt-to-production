# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint to determine its category and priority level, providing a justified reason and an optional flag for review.
    input: String (the complaint description text).
    output: Structured record containing category (from taxonomy), priority (Urgent/Standard/Low), reason (single sentence), and flag (NEEDS_REVIEW or blank).
    error_handling: If the description is empty or excessively vague, categorize as 'Other' and set the flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Iterates through a CSV file of complaints, applying the classification logic to each row and generating a consolidated results file.
    input: File path to a CSV containing a list of complaints (e.g., test_pune.csv).
    output: File path to a CSV containing the original descriptions plus the new classification columns (category, priority, reason, flag).
    error_handling: Skips malformed CSV rows and logs errors for individual classification failures to ensure the entire batch is processed.
