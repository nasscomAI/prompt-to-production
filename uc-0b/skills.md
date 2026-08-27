# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: Loads a policy text file and returns its content as structured numbered sections with clause identification.
    input: String parameter file_path (absolute or relative path to .txt policy file). File must use numbered clause structure (e.g., 2.3, 2.4, 3.2).
    output: Dictionary containing 'raw_content' (full text as string) and 'clauses' (list of dictionaries with keys 'clause_number', 'clause_text', 'binding_verb'). Returns structured data for validation and processing.
    error_handling: If file does not exist, raise FileNotFoundError with clear message. If file cannot be parsed or lacks numbered structure, return error dict with 'error' key explaining structural issue. Never proceed with malformed input.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary that preserves all clauses, conditions, and binding obligations with clause references.
    input: Dictionary from retrieve_policy containing 'raw_content' and 'clauses' list. Each clause entry must have 'clause_number', 'clause_text', 'binding_verb'.
    output: String containing the complete summary with format: each clause on new line as "Clause X.Y: [summary preserving all conditions and binding verb]". If verbatim quotes needed, include [VERBATIM_QUOTE_CLAUSE_X.Y] flag.
    error_handling: If input lacks required keys or clause list is empty, return error string explaining missing data. If any clause cannot be safely summarized (complex multi-part obligations), quote verbatim and flag for review. Count clauses in input vs output and warn if mismatch detected.
