# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a policy text file and returns its content structured by numbered clauses.
    input: File path (string) pointing to the policy document.
    output: Parsed representation of the policy with clause numbers and full clause text.
    error_handling: If the file cannot be read or clauses cannot be parsed, returns an error detail and an empty clause map.

  - name: summarize_policy
    description: Produces a compliant summary that preserves all binding obligations and conditions for each required clause.
    input: Structured clauses (from retrieve_policy) and a list of required clause numbers.
    output: A summary text that includes each required clause, preserving meaning and quoting verbatim where necessary.
    error_handling: If a clause is missing or cannot be summarized without meaning loss, include the full original clause and flag it.
