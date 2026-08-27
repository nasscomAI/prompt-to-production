# skills.md

skills:
  - name: retrieve_policy
    description: Load the provided .txt policy document and parse it into structured numbered sections.
    input: File path of the `.txt` source (string).
    output: A dictionary where keys are clause numbers and values are the text of the clause.
    error_handling: Return error if file doesn't exist or if no numbered clauses are found.

  - name: summarize_policy
    description: Summarizes the structured clauses by guaranteeing every numbered clause is included, multiparty conditions are preserved verbatim, and no new phrases are added.
    input: Dictionary of structured policy clauses.
    output: A single string consisting of the valid policy summary with clause references.
    error_handling: Refuses to summarize and returns the verbatim text flagged if the clause cannot be synthesized accurately without meaning loss.
