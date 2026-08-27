# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections for downstream summarisation.
    input: Path to a .txt policy file (e.g. policy_hr_leave.txt).
    output: Structured representation of the document with numbered sections/clauses mapped to their text content.
    error_handling: If the file cannot be read or contains no numbered sections, halt and report the error — do not proceed with empty or partial content.

  - name: summarize_policy
    description: Takes structured numbered sections from retrieve_policy and produces a compliant summary with clause references, preserving all obligations and conditions.
    input: Structured sections object from retrieve_policy containing numbered clauses and their text.
    output: A summary text file containing every clause, its core obligation, all binding conditions preserved, and verbatim quotes where paraphrasing would cause meaning loss.
    error_handling: If any numbered clause is missing from the output, flag it before writing — never produce a summary with silently dropped clauses.
