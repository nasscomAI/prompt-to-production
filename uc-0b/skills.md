# skills.md

skills:
  - name: retrieve_policy
    description: Loads the HR leave policy text file and returns its content as structured numbered sections.
    input: A file path string pointing to the policy text file (e.g. `../data/policy-documents/policy_hr_leave.txt`).
    output: A structured representation of numbered clauses and their text.
    error_handling: If the file is missing, unreadable, or cannot be parsed into numbered sections, return a clear error and halt summarization.

  - name: summarize_policy
    description: Produces a compliant summary from structured policy sections while preserving every numbered clause and condition.
    input: Structured policy sections from `retrieve_policy`, plus optional clause inventory guidance.
    output: A concise summary suitable for `uc-0b/summary_hr_leave.txt` that preserves clause meaning.
    error_handling: If a clause cannot be safely summarized without omission or hallucination, return that clause verbatim and flag the issue instead of inventing details.
