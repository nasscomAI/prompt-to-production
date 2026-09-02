skills:
  - name: retrieve_policy
    description: Loads a plain-text policy file and parses its contents into structured numbered sections and clauses preserving exact clause numbers, headers, and text.
    input: file_path (str) pointing to the policy .txt document on the filesystem.
    output: dict mapping section numbers and titles to lists of parsed clauses, where each clause contains clause_id (str, e.g., '2.3') and clause_text (str).
    error_handling: If the file does not exist, is empty, or cannot be parsed, raises a FileNotFoundError or ValueError with a clear refusal message rather than returning partial or imagined content.

  - name: summarize_policy
    description: Transforms structured policy sections into a complete, non-lossy summary that retains every numbered clause reference, all conditions, exact thresholds, and unsoftened binding verbs.
    input: structured_sections (dict) produced by retrieve_policy containing all parsed sections and clauses.
    output: summary_text (str) formatted as a structured document with section headings and bulleted clauses citing exact IDs (e.g., '[2.3]'), with [VERBATIM_PRESERVED] tags applied where necessary.
    error_handling: If a clause contains complex multi-condition constraints that risk meaning loss during condensation, preserves the clause text verbatim flagged with [VERBATIM_PRESERVED]; rejects any missing or corrupted sections.
