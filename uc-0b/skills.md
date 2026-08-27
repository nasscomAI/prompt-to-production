# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_policy
    description: >
      Loads the HR leave policy text file and converts it into structured
      numbered sections while preserving clause numbering, hierarchy,
      binding verbs, timelines, approval dependencies, and prohibitions.
    input:
      type: file_path
      format: >
        Relative or absolute path to a plain text policy document
        (.txt), such as ../data/policy-documents/policy_hr_leave.txt
    output:
      type: structured_document
      format: >
        YAML or JSON object containing ordered numbered clauses with:
        clause_id, raw_text, binding_verbs, conditions, approvals,
        timelines, and prohibitions.
    error_handling:
      - "Return FILE_NOT_FOUND if the policy file does not exist."
      - "Return INVALID_FORMAT if the input is not a readable .txt file."
      - "Return PARSE_ERROR if numbered clauses cannot be reliably extracted."
      - "Flag missing or malformed clause numbering without guessing structure."
      - "Preserve raw text when structure extraction confidence is low."

  - name: summarize_policy
    description: >
      Generates a compliance-safe summary from structured policy clauses
      while preserving all obligations, conditions, approval chains,
      forfeiture rules, prohibitions, and clause references exactly.
    input:
      type: structured_document
      format: >
        Structured numbered policy sections produced by retrieve_policy,
        including clause identifiers and raw clause text.
    output:
      type: summary_document
      format: >
        Plain text summary with clause references, preserving all mandatory
        conditions and binding meaning from the source policy.
    error_handling:
      - "Return CLAUSE_MISSING if any numbered clause is absent from the summary."
      - "Return CONDITION_DROP_DETECTED if multi-condition obligations are partially summarized."
      - "Return OBLIGATION_SOFTENING if mandatory language is weakened."
      - "Return SCOPE_BLEED if unsupported external assumptions are introduced."
      - "Quote the original clause verbatim and flag it when summarization risks meaning loss."