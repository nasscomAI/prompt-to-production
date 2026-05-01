skills:
  - name: retrieve_policy
    description: Loads a plain-text HR leave policy file and returns structured numbered sections as the ground-truth clause inventory.
    input:
      type: file_path
      format: Relative or absolute path to a UTF-8 `.txt` policy document (expected: `../data/policy-documents/policy_hr_leave.txt`).
    output:
      type: structured_sections
      format: YAML list of objects with `clause_id`, `text`, and `binding_verb`, preserving source order and numbering (including 2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2 when present).
    error_handling:
      - If the file path is invalid, unreadable, or not `.txt`, return `error_code: INVALID_INPUT_FILE` with a clear reason and no inferred content.
      - If numbered sections are missing, malformed, or ambiguous, return `error_code: AMBIGUOUS_STRUCTURE` and list unresolved spans for user correction.
      - If required clause IDs from the UC inventory are absent, return `error_code: CLAUSE_INVENTORY_MISMATCH` with missing clause IDs.
      - If content appears to come from multiple mixed sources, return `error_code: SCOPE_BLEED_RISK` and refuse to merge unverified text.

  - name: summarize_policy
    description: Converts structured policy sections into a compliant clause-referenced summary without semantic loss.
    input:
      type: structured_sections
      format: YAML/JSON array of numbered clause objects from `retrieve_policy`, each containing `clause_id`, `text`, and optional `binding_verb`.
    output:
      type: summary_text
      format: Plain text summary with explicit clause references, suitable for `uc-0b/summary_hr_leave.txt`.
    error_handling:
      - If input is empty, not structured, or lacks clause identifiers, return `error_code: INVALID_SECTION_INPUT` and do not summarize.
      - If any required clause would be omitted, return `error_code: CLAUSE_OMISSION_RISK` with the missing clause IDs.
      - If any multi-condition rule cannot be preserved exactly (including clause 5.2 requiring both Department Head and HR Director approvals), quote the clause verbatim, flag `CONDITION_DROP_RISK`, and avoid softened paraphrase.
      - If generated text introduces unsupported claims or scope-bleed language (e.g., "as is standard practice", "typically in government organisations", "employees are generally expected to"), return `error_code: UNSUPPORTED_ADDITION` and remove the added content.
      - If a clause cannot be summarized without meaning loss, output that clause verbatim with a `FLAG_MEANING_LOSS` marker instead of guessing.
