# skills.md — UC-0B

skills:

  - name: retrieve_policy
    description: Load the provided .txt policy file and return its content as structured numbered sections.
    input: A policy .txt file path containing numbered policy clauses.
    output: A structured collection of numbered sections containing the clause references and source text.
    error_handling: If the file is missing, unreadable, or invalid, report the error and do not invent or reconstruct missing policy content.

  - name: summarize_policy
    description: Produce a compliant policy summary from structured sections while preserving every required clause and all material conditions.
    input: Structured numbered policy sections retrieved from the policy document.
    output: A policy summary containing clause references for all 10 required clauses, with obligations, conditions, approvers, time limits, exceptions, and consequences preserved.
    error_handling: If a clause cannot be summarized without meaning loss, quote it verbatim and flag it for review rather than guessing or omitting it.