# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns content as structured numbered sections.
    input: Path to policy file (str)
    output: Dictionary with section numbers as keys and content as values
    error_handling: If file not found, raise FileNotFoundError. If file is empty, return empty dict.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary with clause references.
    input: Dictionary of policy sections (dict)
    output: String containing summary with all clauses preserved
    error_handling: If sections are empty, return "No policy content to summarize."
