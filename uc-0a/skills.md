# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Analyzes a single complaint description to determine its category, priority, and justification based on defined roles and enforcement rules.
    input: A complaint description string from the citizen input.
    output: A structured object containing: category, priority, reason (one sentence citing input text), and flag (NEEDS_REVIEW or blank).
    error_handling: Handles ambiguous or nonsense descriptions by categorizing as 'Other' and setting the flag field to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Orchestrates the end-to-end processing of a batch of complaints by reading from an input CSV, applying the classification skill, and saving results to an output CSV.
    input: File paths for both the input CSV (source of complaints) and output CSV (destination for results).
    output: A new CSV file containing the original descriptions plus the four new classification fields.
    error_handling: Validates the existence and format of the input file and ensures that the output file is correctly written according to the schema.
