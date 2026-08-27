# skills.md — UC-0B Policy Summary System

skills:
  - name: load_policy_document
    description: Loads and parses a policy document into structured numbered sections.
    input: File path (string) to the policy document text file.
    output: Dictionary mapping section numbers (e.g., "2.3", "5.2") to section text content, plus metadata (document title, version, effective date).
    error_handling: If file not found, raises FileNotFoundError. If document has no numbered sections, returns empty dict with warning.

  - name: extract_numbered_clauses
    description: Extracts all numbered clauses from the policy document and returns them as a list for verification.
    input: Dictionary of sections from load_policy_document.
    output: List of tuples (section_number, section_text) in document order.
    error_handling: Returns empty list if no sections found. Does not fail - used for validation.

  - name: identify_multi_condition_clauses
    description: Identifies clauses containing multiple conditions joined by AND/OR to ensure no condition dropping.
    input: Dictionary of sections from load_policy_document.
    output: List of section numbers that contain multi-condition requirements (e.g., ["5.2", "2.4"]).
    error_handling: Returns empty list if no multi-condition clauses found.

  - name: summarize_clause
    description: Summarizes a single policy clause while preserving all conditions and obligation verbs.
    input: Section number (string), section text (string), list of multi-condition section numbers.
    output: Summarized text with section number citation, or verbatim quote if too complex to summarize safely.
    error_handling: If clause contains multiple conditions and summarization would risk dropping one, returns verbatim quote with [VERBATIM] flag.

  - name: generate_policy_summary
    description: Generates complete policy summary by processing all clauses and validating completeness.
    input: Dictionary of sections from load_policy_document.
    output: String containing full summary with all numbered clauses, citations, and any verbatim quotes flagged.
    error_handling: Validates that output clause count matches input clause count. If mismatch, raises ValueError listing missing clauses.

  - name: validate_summary_completeness
    description: Validates that summary contains all source clauses and preserves conditions.
    input: Original sections dictionary, generated summary string.
    output: Tuple (is_valid: bool, missing_clauses: list, dropped_conditions: list).
    error_handling: Always returns a result - never fails. Use output to decide if summary is acceptable.
