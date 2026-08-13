# skills.md

skills:
  - name: retrieve_policy
    description: Loads a raw policy text file and parses it into structured sections and numbered clauses.
    input: File path input_path (string path to policy .txt file).
    output: Dictionary mapping section headings and clause numbers (e.g., '2.3', '5.2') to their exact text.
    error_handling: Raises FileNotFoundError if input path is invalid; flags unnumbered paragraphs as general context.

  - name: summarize_policy
    description: Takes structured policy sections and generates a compliant, clause-mapped summary enforcing RICE rules.
    input: Dictionary of structured policy clauses from retrieve_policy.
    output: Formatted string summary mapping each section and clause with its binding rules, dual approvals, and exclusions.
    error_handling: If a clause contains complex dual conditions that risk meaning loss during compression, quotes the clause verbatim with an explicit [VERBATIM] tag.
