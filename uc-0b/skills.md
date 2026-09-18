# skills.md

skills:
  - name: retrieve_policy
    description: Loads one policy text file and returns structured numbered clauses with complete clause text.
    input: input_path string to a .txt policy document.
    output: Ordered list of clause objects with clause_number and clause_text.
    error_handling: If file missing or unreadable, return a clear load error and stop without generating synthetic policy content.

  - name: summarize_policy
    description: Produces a clause-preserving summary with clause references from structured policy clauses.
    input: Ordered list of clause objects from retrieve_policy.
    output: Plain-text summary where each numbered clause is represented once with preserved obligations.
    error_handling: If any clause is ambiguous for safe compression, output that clause verbatim and mark [VERBATIM].
