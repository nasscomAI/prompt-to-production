

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and parses it into structured numbered sections.
    input: String path to the input .txt file.
    output: Dictionary where keys are clause numbers (e.g., "2.3") and values are the text of the clause.
    error_handling: Returns an empty dictionary and logs an error if the file is missing, unreadable, or contains no numbered clauses.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary with clause references while preserving all obligations and conditions with RICE Enforcement rules.
    input: Dictionary of numbered policy sections.
    output: String containing the summarized policy with clause references and [PRECISION_REQUIRED] flags where applicable.
    error_handling: If a section cannot be safely summarized without meaning loss or malformed, it must be quoted verbatim and flagged as [PRECISION_REQUIRED] instead of being omitted for manual review.