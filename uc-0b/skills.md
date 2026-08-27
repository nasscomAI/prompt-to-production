# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: Loads HR leave policy .txt file and returns content as structured numbered sections with clause identifiers.
    input: "File path to policy_hr_leave.txt (string)"
    output: "Dict with keys: raw_text (full document string), sections (dict mapping clause_id → clause_text), clause_list (list of clause IDs in order: 2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2)"
    error_handling: "If file not found, raise FileNotFoundError with path. If file is empty or malformed, return raw_text only and empty sections dict. Never skip malformed clauses—flag them for manual review."

  - name: summarize_policy
    description: Takes structured policy sections and produces compliance-preserving summary with all 10 clauses preserved, multi-conditions intact, and scope bleed prevented.
    input: "Dict with keys: sections (dict clause_id → clause_text), clause_list (ordered list of clause IDs)"
    output: "Dict with keys: summary (summary text), clause_coverage (list of clause IDs found in summary), preserved_verbatim (list of {clause_id, text, reason} for [PRESERVE_VERBATIM] flags), compliance_flags (list of violations if any: CLAUSE_OMISSION, CONDITION_DROP, BINDING_VERB_SOFTENING, SCOPE_BLEED)"
    error_handling: "If any of the 10 clauses is missing from summary, add to compliance_flags: CLAUSE_OMISSION. If multi-condition clause drops a condition, add: CONDITION_DROP. If scope bleed detected, add: SCOPE_BLEED. If binding verb softened (e.g., 'must' → 'can'), add: BINDING_VERB_SOFTENING. Always produce output even with flags; never fail silently."
