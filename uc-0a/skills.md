# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: [classify_complaint]
    description: [classifies a citizen complaint into the correct category and priority level]
    input: [a text description of the citizen complaint ]
    output: [Category, priority level, reason for classification, and optional flag.]
    error_handling: [ If the complaint is unclear or ambiguous, return the flag NEEDS_REVIEW.]

  - name: [batch_classify]
    description: [Reads a CSV file of complaints and classifies each complaint using the classification rules.]
    input: [ CSV file containing multiple complaint descriptions.]
    output: [CSV file with category, priority, reason, and flag for each complaint.]
    error_handling: [If the CSV format is incorrect, return an error message.]
