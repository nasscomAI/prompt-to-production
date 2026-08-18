# skills.md

skills:
  - name: retrieve_policy
    description: Loads the .txt policy file and returns content as structured numbered sections.
    input: File path (string) to the policy .txt file.
    output: Dictionary of structured sections (e.g., {'2.3': 'content', ...}).
    error_handling: If file not found, raise FileNotFoundError.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references.
    input: Structured sections (dictionary).
    output: Summary text (string) including all clauses.
    error_handling: If sections are invalid or incomplete, raise ValueError.
