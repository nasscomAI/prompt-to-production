skills:
  - name: retrieve_policy
    description: Loads raw .txt policy document and parses content into structured numbered sections and clauses.
    input: File path string (e.g., ../data/policy-documents/policy_hr_leave.txt)
    output: Dictionary mapping section titles and clause numbers to raw clause text string.
    error_handling: Raises FileNotFoundError if file is missing; raises ValueError if document contains no numbered clauses.

  - name: summarize_policy
    description: Takes structured policy clauses and generates a compliant summary adhering strictly to RICE enforcement rules.
    input: Parsed policy dictionary containing numbered clauses and metadata.
    output: Markdown formatted policy summary string containing explicit clause mappings, exact conditions, and zero scope bleed.
    error_handling: Flags missing clauses with [MISSING_CLAUSE] and flags ambiguous/unsummarizable clauses with [VERBATIM_REQUIRED].
