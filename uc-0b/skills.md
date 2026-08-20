skills:
  - name: retrieve_policy
    description: >
      Loads a leave-policy .txt file and returns a structured clause inventory
      with normalized numbered sections and extracted obligation metadata.
    purpose: >
      Establish immutable ground truth before summarization so downstream logic
      cannot omit clauses, soften obligations, or lose multi-condition rules.
    input:
      type: object
      required_fields:
        - input_path
      constraints:
        - input_path must point to a readable UTF-8 text file.
        - File must contain numbered policy clauses.
    output:
      type: object
      required_fields:
        - source_text
        - sections
        - required_clause_inventory
        - retrieval_warnings
      sections_schema:
        - clause_id
        - raw_text
        - normalized_text
        - binding_verb
        - extracted_conditions
        - extracted_deadlines
        - extracted_approvals
        - extracted_consequences
      required_clause_inventory:
        required_ids:
          - "2.3"
          - "2.4"
          - "2.5"
          - "2.6"
          - "2.7"
          - "3.2"
          - "3.4"
          - "5.2"
          - "5.3"
          - "7.2"
        status_per_clause:
          - found
          - missing
          - partial
    processing_contract:
      extraction_steps:
        - Read full file content without rewriting legal text.
        - Parse numbered clauses and retain clause identifiers.
        - Extract binding verbs exactly as present (must/will/requires/not permitted).
        - Extract critical constraints (dates, thresholds, windows, required approvers, consequences).
      normalization_rules:
        - Preserve legal meaning; normalize whitespace only.
        - Keep original clause text available for verbatim fallback.
      quality_checks:
        - Confirm all 10 required clauses are present or flagged missing/partial.
        - Flag clauses with potentially ambiguous parse boundaries for manual review.
    error_handling:
      file_errors:
        - If file missing/unreadable, raise explicit error with input_path.
      parse_errors:
        - If numbered parsing fails, return best-effort sections plus retrieval_warnings and mark unparsed regions.
      integrity_errors:
        - If required clause IDs are missing, do not guess content; mark as missing in inventory.

  - name: summarize_policy
    description: >
      Converts structured policy sections into a clause-faithful summary that
      preserves all required obligations, conditions, and binding strength.
    purpose: >
      Generate a concise summary without meaning drift by enforcing explicit
      coverage, condition preservation, and no-addition constraints.
    input:
      type: object
      required_fields:
        - sections
        - required_clause_inventory
      optional_fields:
        - source_text
      constraints:
        - sections must include clause IDs and raw text.
        - required_clause_inventory must include the 10 UC-0B clause IDs.
    output:
      type: object
      required_fields:
        - summary_text
        - clause_trace
        - compliance_report
      clause_trace_schema:
        - clause_id
        - source_excerpt
        - summary_line
        - preservation_status
      compliance_report_fields:
        - total_required_clauses
        - covered_clauses
        - missing_clauses
        - softened_obligations
        - dropped_conditions
        - added_non_source_content
        - review_required_clauses
    summarization_contract:
      coverage:
        - Must include all required clause IDs (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2).
      meaning_preservation:
        - Preserve all conditions in multi-condition clauses.
        - Preserve all approvers in approval-chain clauses.
        - Preserve thresholds/time windows/deadlines exactly.
        - Preserve explicit consequences (LOP, forfeiture, prohibition).
      binding_strength:
        - Do not weaken mandatory verbs into advisory language.
      no_scope_bleed:
        - Do not introduce external norms, generic HR phrasing, or inferred exceptions.
      fallback_behavior:
        - If paraphrase risks meaning loss, quote the clause verbatim and tag REVIEW_REQUIRED.
        - If clause text missing/unclear, emit REVIEW_REQUIRED for that clause instead of guessing.
    validation_gates:
      gate_1_clause_completeness:
        - Fail if any required clause missing from summary.
      gate_2_condition_integrity:
        - Fail if any condition, approver, threshold, or deadline from source is absent in summary line.
      gate_3_binding_verb_integrity:
        - Fail if mandatory/prohibitive language is softened.
      gate_4_source_only_check:
        - Fail if summary adds unsupported statements.
      gate_5_review_routing:
        - Route high-risk lines to REVIEW_REQUIRED instead of emitting uncertain paraphrases.
    error_handling:
      invalid_input:
        - Return structured failure with compliance_report indicating non-runnable state.
      validation_failure:
        - Return summary plus explicit compliance failures and REVIEW_REQUIRED flags.
      hard_failure:
        - Raise actionable error only for unrecoverable structural issues (for example, missing sections object).
