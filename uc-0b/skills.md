# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured, numbered sections.
    input: Path to the policy .txt file (string).
    output: A collection of structured policy sections (list or dictionary).
    error_handling: Returns a specific error message if the file is missing or contains invalid formatting.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary with explicit clause references.
    input: Structured policy sections (list or dictionary).
    output: A formatted summary string preserving all core obligations and binding verbs.
    error_handling: Flags sections that are too complex to summarize for verbatim quoting and review.
