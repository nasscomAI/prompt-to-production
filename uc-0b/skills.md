# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a policy text file and parses it into structured numbered clauses.
    input: File path to policy document (e.g. policy_hr_leave.txt).
    output: Dictionary mapping section and clause numbers to raw clause text.
    error_handling: Raises FileNotFoundError if file is missing or unreadable.

  - name: summarize_policy
    description: Generates a complete, clause-preserving summary from structured policy sections.
    input: Structured policy dictionary from retrieve_policy.
    output: Formatted summary text file preserving all 10 critical clauses and multi-approver obligations.
    error_handling: Flags clauses requiring exact verbatim inclusion if summarization risks losing precision.

