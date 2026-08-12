skills:
  - name: retrieve_policy
    description: Parses a plain-text policy file into structured numbered sections and individual clauses with metadata (clause id, section title, text).
    input: file_path (str path to policy .txt file)
    output: dict containing document metadata and list of structured sections/clauses
    error_handling: Raises FileNotFoundError if file is missing; handles irregular whitespace and encoding gracefully.

  - name: summarize_policy
    description: Processes structured policy clauses into an audited summary that enforces all 10 core obligations, preserves dual approver requirements, and retains verbatim references without scope bleed.
    input: structured_policy (dict containing parsed sections and clauses)
    output: formatted_summary (str representing the complete audited policy summary)
    error_handling: Validates that all critical clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) are present; flags any unmapped clauses.
