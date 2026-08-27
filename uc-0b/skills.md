# skills.md

skills:
  - name: retrieve_policy
    description: Loads a policy text file and extracts numbered clauses into a structured mapping.
    input: A path to a .txt policy file.
    output: A dictionary mapping clause IDs such as 2.3 to the corresponding text.
    error_handling: Returns an empty mapping if the file is missing or unreadable.

  - name: summarize_policy
    description: Produces a clause-preserving summary for the required policy clauses.
    input: A dictionary of extracted policy clauses.
    output: A plain-text summary with one line per required clause.
    error_handling: Includes a placeholder for any missing clause rather than inventing content.
