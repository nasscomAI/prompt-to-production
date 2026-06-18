skills:
  - name: retrieve_policy
    description: Loads a policy text file and returns its numbered clauses as structured sections with clause ids and clause text.
    input: A path to a UTF-8 plain text policy document.
    output: A list of section dictionaries with clause, text, and source_file fields in source order.
    error_handling: Rejects missing or unreadable files with a clear error and rejects documents that contain no numbered clauses.

  - name: summarize_policy
    description: Produces a clause-complete summary that preserves every numbered obligation and keeps each clause reference in the output.
    input: A list of structured policy sections containing clause ids and clause text.
    output: A plain text summary that includes every numbered clause exactly once with its clause reference.
    error_handling: If a clause cannot be reduced safely, quotes the clause text verbatim and flags it inline instead of dropping or softening conditions.
