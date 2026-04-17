# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: Loads a policy document file, parses numbered sections, and returns structured content with section references preserved.
    input: path to .txt policy file.
    output: dict with keys document_name and sections (list of dicts with section_number, section_title, and section_text).
    error_handling: If file not found or malformed, raises exception with file path and error reason. If sections cannot be parsed, returns raw text with warning.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary preserving all clauses, conditions, and binding verbs exactly.
    input: dict with sections (from retrieve_policy) and mandatory_clauses list (clauses that MUST appear).
    output: text summary with all mandatory clauses cited by section number, multi-conditions preserved, and flags for quoted/ambiguous clauses.
    error_handling: If any mandatory clause is missing from source, flags as MISSING. If clause has conflicting conditions, quotes verbatim. If clause cannot be simplified without loss, flags as NEEDS_REVIEW.
