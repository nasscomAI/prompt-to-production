skills:
  - name: retrieve_policy
    description: Load the supplied HR leave policy text and organize its numbered clauses into structured sections.
    input: A UTF-8 text policy file path.
    output: Structured policy sections keyed by their original clause numbers, preserving the source wording and conditions.
    error_handling: If the file cannot be read or contains no numbered policy clauses, return an error instead of inventing content.

  - name: summarize_policy
    description: Produce a clause-referenced summary that preserves every obligation, condition, exception, deadline, limit, and approval requirement.
    input: Structured numbered policy sections produced by retrieve_policy.
    output: A plain-text summary containing every numbered clause and its faithful summary.
    error_handling: If any clause is ambiguous or cannot be summarized without meaning loss, quote that clause verbatim and mark it for review rather than guessing.