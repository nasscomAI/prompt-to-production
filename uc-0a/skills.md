# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: [classify_complaint]
    description: Classifies a single civic complaint into category, priority, reason, and review flag.
    input: A string containing the complaint description text.
    output: A dictionary with fields {category: string, priority: string, reason: string, flag: string}.
    error_handling: If the description is empty or unclear, assigns category "Other" and sets flag to "NEEDS_REVIEW".

  - name: [batch_classify]
    description: Processes a CSV file of complaints and generates a structured classification output CSV.
    input: CSV file with at least a "description" column.
    output: CSV file with columns [complaint_id, description, category, priority, reason, flag].
    error_handling: Skips rows with missing description or marks them as "Other" with "NEEDS_REVIEW".
