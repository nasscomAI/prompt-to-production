# skills.md — UC-0B Policy Summariser

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections and clauses.
    input: file path (string) to a policy .txt file.
    output: list of sections, each with a title and an ordered list of clauses (num, text).
    error_handling: Missing file raises a clear error naming the file; unparseable lines are preserved verbatim, never dropped.

  - name: summarize_policy
    description: Produces a compliant summary from structured sections, preserving every clause and every condition verbatim with its clause number.
    input: structured sections from retrieve_policy.
    output: summary text written to the output file; every clause present, plus a compliance check of the 10 critical clauses.
    error_handling: If a parsed clause has empty text it is flagged rather than silently omitted; exits with an error if any critical clause is missing.
