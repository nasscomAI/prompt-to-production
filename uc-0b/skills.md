skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: File path to a HR policy text file (String).
    output: A structured representation of the policy document parsed by numbered sections and clauses.
    error_handling: Return a clear error if the file is missing, unreadable, or not formatted with clear numbered clauses.

  - name: summarize_policy
    description: Takes structured clauses and produces a compliant summary that strictly preserves all meaning, multi-condition obligations, and rules from the source.
    input: Structured policy sections and clauses (List/JSON).
    output: A compliance-checked summary string including exact clause references, with zero additions or knowledge assumptions.
    error_handling: Flag the clause and quote it verbatim if it is determined that a clause cannot be reliably summarised without losing conditions or meaning loss.
