# skills.md — UC-0B Policy Summarization Skills

skills:
  - name: retrieve_policy
    description: Parses a plain text policy document into structured components by identifying section headings and numbered clauses.
    input: String (absolute path to the .txt policy file).
    output: List of dictionaries, each containing 'clause_id' and 'text'.
    error_handling: Raises FileNotFoundError if the file is missing; returns an empty list if no numbered clauses are found.

  - name: summarize_policy
    description: Transforms structured policy clauses into a condensed summary while strictly preserving all obligations, binding verbs, and multiple approval conditions.
    input: List of structured clause dictionaries.
    output: String (the formatted summary).
    error_handling: If a clause cannot be summarized without losing strict meaning, it is quoted verbatim and flagged.
