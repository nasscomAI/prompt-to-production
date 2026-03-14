# skills.md

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
