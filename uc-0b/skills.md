
# skills.md

skills:

  - name: summarize_leave_policy
    description: Summarizes the required HR leave policy clauses while preserving their conditions and exceptions.
    input: HR leave policy document as a text file.
    output: Concise text summary containing the required policy clauses and their clause numbers.
    error_handling: If required policy information is missing or ambiguous, preserve the available information and flag the affected clause as NEEDS_REVIEW.

  - name: validate_leave_summary
    description: Checks that the generated summary contains the required policy clauses and does not omit important conditions.
    input: Generated HR leave policy summary as text.
    output: Validation result identifying missing or potentially incomplete clauses.
    error_handling: Flag missing, ambiguous, or incomplete clauses as NEEDS_REVIEW instead of silently accepting them.