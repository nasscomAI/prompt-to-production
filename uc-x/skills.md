skills:
  - name: retrieve_documents
    description: >
      Loads all policy text files and builds a section-level index keyed by
      document name and section number for deterministic retrieval.
    purpose: >
      Ensure all downstream answers are anchored to explicit source sections
      and can be traced to one document section without blending.
    input:
      type: object
      required_fields:
        - document_paths
      constraints:
        - Must include exactly these documents:
          - policy_hr_leave.txt
          - policy_it_acceptable_use.txt
          - policy_finance_reimbursement.txt
    output:
      type: object
      required_fields:
        - document_index
        - metadata
      document_index_schema:
        - document_name
        - section_id
        - section_text
      metadata_fields:
        - loaded_documents
        - section_count
        - parse_warnings
    processing_contract:
      - Parse numbered sections in each document and keep continuation lines.
      - Preserve original section text for citation fidelity.
      - Normalize whitespace only; do not rewrite policy language.
    error_handling:
      file_errors:
        - Raise explicit error when any required document is missing/unreadable.
      parse_errors:
        - Return parse warnings and best-effort index; never fabricate missing section text.

  - name: answer_question
    description: >
      Answers a user question using one best-matching policy section from one
      document, with citation, or returns the exact refusal template.
    purpose: >
      Prevent cross-document blending and hedged hallucinations by enforcing
      single-source output and deterministic refusal behavior.
    input:
      type: object
      required_fields:
        - question
        - document_index
      constraints:
        - question must be non-empty.
    output:
      type: object
      required_fields:
        - answer_text
        - citation
        - mode
      mode_allowed:
        - ANSWER
        - REFUSAL
      citation_format:
        - document_name + section_id for ANSWER mode
        - blank for REFUSAL mode
    selection_rules:
      - Rank candidate sections by lexical relevance to question.
      - Select exactly one best section from one document for ANSWER mode.
      - If no adequate support exists, output exact refusal template.
      - If top support ties across documents or requires combining claims, output refusal template.
    response_rules:
      - In ANSWER mode, include only claims present in selected section text.
      - Do not use prohibited hedging phrases.
      - Do not include inferred company practices or unstated permissions.
      - For policy constraints, preserve explicit limits and prohibitions.
    refusal_template_exact: |
      This question is not covered in the available policy documents
      (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
      Please contact [relevant team] for guidance.
    error_handling:
      invalid_input:
        - Return REFUSAL when question is empty or index unavailable.
      ambiguity:
        - Return REFUSAL when single-source resolution cannot be established with confidence.
      hard_failure:
        - Raise actionable error only for unrecoverable index corruption.
