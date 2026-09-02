# skills.md

skills:

* name: retrieve_policy
  description: Load the supplied employee leave policy text file and return its contents as structured numbered sections and clauses.
  input: Text file path pointing to the policy document.
  output: Structured list of policy sections containing their numbered clauses and original clause text.
  error_handling: If the file is missing, unreadable, empty, or does not contain usable policy text, report the error and do not invent or infer missing content.

* name: summarize_policy
  description: Produce a compliant policy summary from structured policy clauses while preserving every clause, condition, obligation, exception, threshold, approval requirement, and consequence.
  input: Structured numbered policy sections produced by retrieve_policy.
  output: Plain-text summary containing clause references and faithful summaries of the supplied policy clauses.
  error_handling: If a clause is ambiguous or cannot be summarized without changing its meaning, preserve the clause verbatim and mark it for review instead of guessing.
