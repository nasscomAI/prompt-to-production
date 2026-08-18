skills:
  - name: retrieve_policy
    description: Loads a policy text file and parses it into structured numbered sections.
    input: Path to the .txt policy file.
    output: Structured sections mapping section numbers/clause IDs to their raw text content.
    error_handling: Raises file not found errors if the file doesn't exist, and warns if the text cannot be parsed.

  - name: summarize_policy
    description: Generates a compliant summary from structured sections while referencing all key clauses.
    input: Structured policy sections.
    output: Summary text preserving all 10 key numbered clauses, their binding verbs, and conditions.
    error_handling: Quotes the clause verbatim and highlights it if summarizing it introduces any potential meaning loss or condition drop.
