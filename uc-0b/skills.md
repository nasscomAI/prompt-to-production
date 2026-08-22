skills:
  - name: retrieve_policy
    description: Load the HR leave policy and return its numbered clauses for controlled summarization.
    input: Path to policy_hr_leave.txt as a string.
    output: Structured list of numbered policy clauses containing clause number and source text.
    error_handling: If the file is missing, unreadable, or contains no numbered clauses, raise a clear error rather than inventing policy content.

  - name: summarize_policy
    description: Produce a clause-referenced summary that preserves every required condition and obligation from the source.
    input: Structured list of numbered policy clauses.
    output: Summary text containing every required clause reference and preserving all conditions, approvers, limits, dates, and consequences.
    error_handling: If a clause cannot be safely summarized without losing meaning, preserve the relevant source wording rather than guessing or omitting the clause.