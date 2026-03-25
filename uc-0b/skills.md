skills:

  - name: extract_policy_rules
    description: Extracts the important policy rules, conditions, and obligations from the HR leave policy.
    input: Plain text HR policy document.
    output: Structured list of important policy points including leave types, eligibility, approvals, and restrictions.
    error_handling: If the input is empty or unreadable, return an error stating that policy text could not be processed.

  - name: generate_faithful_summary
    description: Produces a concise summary while preserving the original meaning and obligations of the policy.
    input: Structured policy points extracted from the source text.
    output: Clear, human-readable summary of the HR leave policy.
    error_handling: If important clauses are missing or input is ambiguous, summarize only the available verified content and avoid assumptions.

  - name: preserve_policy_constraints
    description: Ensures the summary does not weaken, distort, or omit mandatory clauses and conditions.
    input: Original policy text and generated summary.
    output: Validated summary aligned with the source policy.
    error_handling: If the summary changes meaning or misses major obligations, flag it for correction instead of returning unsafe output.
