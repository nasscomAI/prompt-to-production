skills:
  - name: classify_complaint
    description: Analyzes citizen complaint text and assigns category, priority, and reason.
    input:
      complaint_id: string
      description: string
    output:
      category: string
      priority: string
      reason: string
    error_handling: Return category as Other if input description is ambiguous or unknown.

  - name: flag_ambiguity
    description: Flags complaints requiring human review if multiple categories apply.
    input:
      description: string
    output:
      flag: string
    error_handling: Default flag to NONE if category match is clear.