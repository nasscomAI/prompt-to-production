# skills.md — UC-0B HR Leave Policy Summarizer

skills:
  - name: summarize_leave_policy
    description: Produce a complete and faithful summary of the HR leave policy while preserving all operational requirements, conditions, limits, deadlines, approvals, prohibitions, exceptions, and consequences.
    input: Plain-text HR leave policy document.
    output: Structured summary covering all eight policy sections with exact operational details preserved.
    error_handling: If the source document is missing, incomplete, or ambiguous, do not invent information; identify the missing or ambiguous content explicitly.

  - name: validate_policy_summary
    description: Check a generated policy summary against the source document for omitted, weakened, or generalized operational clauses.
    input: Source HR leave policy text and generated policy summary.
    output: Validation result identifying missing, altered, or weakened requirements and confirming preserved numerical values, conditions, approvals, prohibitions, and consequences.
    error_handling: Report every detected discrepancy explicitly and require correction rather than silently accepting an incomplete summary.