# skills.md
# UC-0B Policy Summarizer Skills
# Each skill is a discrete, testable function that enforces one failure-mode guard.

skills:
  - name: extract_numbered_clauses
    description: Parse policy document and extract all numbered clause sections (2.3, 2.4, etc.) with their exact text.
    input: String — full policy document text.
    output: Dictionary mapping clause_id → (section_number, binding_verb, obligation_text, source_line_range).
    error_handling: If a clause section is malformed or unreadable, mark it [PARSE_ERROR: clause_id reason] and continue. Do not skip.

  - name: preserve_multi_condition_obligations
    description: Detect clauses with multiple conditions (AND, both, require X and Y) and ensure all conditions are preserved in output.
    input: Dictionary of extracted clauses (from extract_numbered_clauses).
    output: List of clause_ids with multi-conditions and a verification that all sub-conditions are present.
    error_handling: If a clause has ambiguous condition structure (e.g., unclear whether "or" is inclusive), flag as [CONDITION_UNCLEAR: clause_id ambiguity_description].

  - name: check_binding_verb_strength
    description: Verify that binding verbs in the summary match the source (must/may/requires/not permitted remain unchanged).
    input: Tuple (clause_id, source_verb, summary_verb).
    output: Boolean (True if verbs match in strength; False if weakened or strengthened) and explanation.
    error_handling: If verb match is ambiguous (e.g., "should" vs "must"), return False and explain why they differ.

  - name: verify_no_clause_omission
    description: Confirm that all numbered clauses from the source document appear in the summary output.
    input: Set of source_clause_ids, Set of summary_clause_ids.
    output: Missing clause list (empty if complete) and presence count (e.g., 10/10 clauses found).
    error_handling: If any clause is missing, return the missing_clause_id list and raise an exception; do not silently continue.

  - name: generate_summary_output
    description: Format the verified clauses into a readable summary text file with clause numbers, obligations, and source attribution.
    input: Dictionary of verified (clause_id, obligation_text, binding_verb, source_section).
    output: String — formatted summary text ready to write to output file.
    error_handling: If input contains [UNCLEAR] or [ERROR] flags, include them in output and do not suppress them.
