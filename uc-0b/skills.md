skills:
  - name: retrieve_policy
    description: Loads the HR leave policy .txt file and returns it as structured numbered sections.
    input: Path to a .txt policy file (string)
    output: Structured sections of the policy with clause numbers and text (list of dicts)
    error_handling: Raises an error if file not found or unreadable; validates numbered clauses

  - name: summarize_policy
    description: Produces a compliant summary of the structured policy sections preserving all obligations.
    input: Structured policy sections (list of dicts)
    output: Summary text with clause references (string)
    error_handling: If a clause cannot be summarised without meaning loss, quotes it verbatim and flags it