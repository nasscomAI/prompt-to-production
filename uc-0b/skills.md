skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content structured into numbered sections (clauses) with section boundaries preserved.
    input:
      type: file
      format: "Plain text policy document (.txt) with numbered sections (e.g., 2.3, 2.4, 5.2)"
      required_field: file_path
    output:
      type: object
      format: "Dictionary mapping clause numbers to full clause text including all conditions and binding verbs"
      schema:
        clauses: dict[str, str]
        total_clauses: int
        metadata: dict
    error_handling:
      - If file not found, return error with file path
      - If file is empty, return error "Policy file is empty"
      - If file is not UTF-8 or plain text, return error "Invalid file format"
      - If numbered sections cannot be parsed, return error "Could not extract numbered clauses"
      - If any of the required 10 clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) are missing from source, return warning with list of missing clauses but continue processing

  - name: summarize_policy
    description: Takes structured policy sections and produces a faithful summary that preserves all 10 clauses with exact conditions, binding language, and obligation strength intact.
    input:
      type: object
      format: "Dictionary of structured clauses from retrieve_policy with clause numbers as keys and full text as values"
      required_field: clauses
    output:
      type: string
      format: "Text summary with all 10 clauses present, clause numbers preserved, conditions preserved, no scope bleed or generalizations"
    error_handling:
      - If input is empty or missing clauses field, return error "Invalid input structure"
      - If any of the 10 required clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) are missing from input, return error with list of missing clauses and refuse to generate summary
      - If clause 5.2 text is present but does not contain both "Department Head" AND "HR Director", flag with warning "[CONDITION DROP DETECTED]"
      - If any multi-condition obligation (2.4, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3) drops a condition, flag with warning "[CONDITION DROP DETECTED]"
      - If summary contains scope bleed phrases ("as is standard practice", "typically", "generally expected", "commonly in government", "employees are generally", "as is customary"), reject summary and return error "Scope bleed detected"
      - If summary omits any clause entirely, return error "Summary missing clause [X.Y]"
      - If summary softens obligation language (changes "must" to "should", "requires" to "may", "not permitted" to "discouraged"), reject and return error "Obligation softening detected in clause [X.Y]"
      - If clause cannot be summarized without meaning loss (determined by comparing word-for-word), quote the clause verbatim and flag with [QUOTED]
      - Validate output against source text before returning — all 10 clauses must be verifiable word-for-word in source

