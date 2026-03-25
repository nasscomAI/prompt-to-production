skills:
  - name: policy_summary_generator
    description: Generates a structured summary of the HR leave policy that includes all numbered clauses and preserves all obligations and conditions.
    input: String content of the policy document file.
    output: Formatted text summary as a string, organized by policy sections.
    error_handling: Raises ValueError if input content is empty, not readable, or does not contain expected policy structure (e.g., no numbered clauses).
