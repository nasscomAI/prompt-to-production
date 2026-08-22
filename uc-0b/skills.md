# skills.md

skills:

  - name: retrieve_policy
    description: Loads the supplied policy text file and returns its numbered clauses as structured sections.
    input: A policy text file path containing a numbered policy document.
    output: A structured collection of policy sections and clauses, preserving clause numbers and original text.
    error_handling: If the file is missing, unreadable, or contains invalid input, return an error without inventing policy content.

  - name: summarize_policy
    description: Produces a compliant policy summary that preserves every numbered clause, its conditions, obligations, limits, exceptions, and consequences.
    input: Structured policy sections returned by retrieve_policy.
    output: A text summary containing every numbered clause with its clause reference and preserved meaning.
    error_handling: If a clause cannot be safely summarized without meaning loss, reproduce it verbatim and flag it for review; never silently omit the clause.