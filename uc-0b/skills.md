skills:
  - name: assignment_analysis
    description: Analyzes an assignment and identifies its requirements, objectives, constraints, and expected deliverables.
    input: Assignment text provided in plain text or Markdown format.
    output: A structured analysis containing requirements, objectives, constraints, and deliverables.
    error_handling: If the assignment is incomplete or ambiguous, identify the missing information and avoid making unsupported assumptions.

  - name: assignment_planning
    description: Creates a clear step-by-step plan for completing an assignment based on its requirements.
    input: Assignment analysis provided in structured text or YAML format.
    output: An ordered step-by-step plan with tasks, priorities, and expected results.
    error_handling: If requirements are unclear or conflicting, identify the issue and request clarification before creating the plan.