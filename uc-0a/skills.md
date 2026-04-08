skills:

name: classify_complaint
description: Classifies a single complaint into category and priority based on the defined schema.
input: One complaint description string.
output: category, priority, reason, and flag.
error_handling: If the complaint description is unclear or ambiguous, assign category "Other" and set flag "NEEDS_REVIEW".

name: batch_classify
description: Processes an input CSV file and applies complaint classification to each row.
input: CSV file containing complaint descriptions.
output: CSV file with category, priority, reason, and flag for each complaint.
error_handling: If a row has missing or invalid description text, classify as "Other" and flag NEEDS_REVIEW.# skills.md

skills:
  - name: classify_complaint
    description: Classifies a civic complaint text into a specific standardized category.
    input: String representing the user complaint text.
    output: String representing the determined category.
    error_handling: Returns "Other" with a "NEEDS_REVIEW" flag if the category cannot be evaluated.

  - name: determine_priority
    description: Analyzes a complaint text to assign a Priority level (e.g., Urgent, High, Medium, Low).
    input: String representing the user complaint text.
    output: String representing the assigned Priority level.
    error_handling: Defaults to "Medium" if no explicit priority keywords are matched.
