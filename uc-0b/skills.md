# skills.md

skills:
  - name: retrieve_policy
    description: Opens the specified .txt file and extracts all numbered sections while preserving formatting and structure.
    input: String representing the absolute or relative file path.
    output: List of dictionaries, each containing 'clause_id' (e.g., '2.3') and 'text'.
    error_handling: Raise an exception if the file cannot be found or read. Return an empty list if no clauses match the expected pattern.

  - name: summarize_policy
    description: Iterates through defined clauses and generates a condensed bulleted list, ensuring verbatim condition retention and no external data hallucination.
    input: List of dictionaries produced by `retrieve_policy`.
    output: A single formatted markdown string summarizing all clauses.
    error_handling: Append the clause verbatim with a `[VERBATIM]` flag if summarization rules (like multi-approver logic) fail to apply neatly.
