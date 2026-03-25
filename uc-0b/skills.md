skills:
  - name: policy_summarizer
    description: Creates a concise and accurate summary of a policy document without changing obligations, conditions, or approvals.
    input: Plain text policy document.
    output: Clear summary text preserving all important rules, constraints, and exceptions.
    error_handling: If the policy text is missing, incomplete, or unclear, do not guess. Return a request for complete or clearer input.

  - name: clause_preserver
    description: Detects and preserves critical clauses such as deadlines, approvals, eligibility rules, exceptions, and restrictions.
    input: Policy or procedural text.
    output: Structured key obligations and constraints that must not be omitted or softened.
    error_handling: If a clause is ambiguous or incomplete, mark it as unclear instead of simplifying it.
