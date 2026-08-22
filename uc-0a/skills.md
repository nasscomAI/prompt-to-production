skills:
  - name: complaint_categorizer
    description: Maps grievance keywords to municipal operational categories.
    input: Raw text string.
    output: String category name.
    error_handling: Defaults to Unclassified if empty.

  - name: severity_priority_evaluator
    description: Enforces escalation rules for civic hazards.
    input: Lowercase text string.
    output: Tuple of priority and reason.
    error_handling: Returns LOW with EMPTY_TEXT flag if empty.