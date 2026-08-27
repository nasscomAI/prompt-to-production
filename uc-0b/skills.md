# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns the content structured by numbered sections.
    input: file_path (Path to .txt file)
    output: List of strings or Dictionary representing numbered sections.
    error_handling: Reports error if file not found or empty.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary that preserves all core obligations and clause references.
    input: sections (Structured data from retrieve_policy)
    output: String (Formatted summary)
    error_handling: Flags missing clauses or ambiguous wording as requiring manual review.
