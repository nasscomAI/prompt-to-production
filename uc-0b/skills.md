    skills:
  - name: analyze_budget
    description: Analyze ward-level budget data and identify spending patterns.
    input: CSV dataset containing ward budgets.
    output: Structured insights about allocation and spending distribution.
    error_handling: If budget fields are missing or invalid, return NEEDS_REVIEW.

  - name: summarize_budget
    description: Generate a concise summary of budget trends from the dataset.
    input: Processed ward budget data.
    output: Text summary highlighting key budget insights.
    error_handling: If dataset cannot be processed, return NEEDS_REVIEW.