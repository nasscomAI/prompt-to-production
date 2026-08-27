skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: File path (string) pointing to a .txt policy document.
    output: List of objects, each with `clause_id` (string like "2.3") and `text` (string — the clause body).
    error_handling: If the file does not exist, raise FileNotFoundError. If the file is empty, return an empty list. If content cannot be parsed into numbered sections, return the raw text in a single entry with clause_id "raw".

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary with clause references, preserving all conditions and binding verbs.
    input: List of objects with `clause_id` and `text` (output of retrieve_policy).
    output: String — the final summary text, written to the output file specified in the run command.
    error_handling: If the input list is empty, return "Policy document contains no clauses to summarise." If required clause is missing from the structured input, flag it with "MISSING CLAUSE [id] — cannot summarise." and stop.
