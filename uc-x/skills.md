# skills.md — UC-X Ask My Documents

skills:
  - name: load_policy_documents
    description: Load all three policy documents into memory with line-by-line indexing.
    input: Directory path containing policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt.
    output: Dictionary mapping document name to (full_text, lines_indexed) for fast searching.
    error_handling: If any document is missing, print warning but continue with available documents. If directory path is invalid, raise error and exit.

  - name: search_documents
    description: Search all policy documents for keywords related to user question, identifying which document(s) contain answer.
    input: User question (string), loaded documents dictionary.
    output: List of tuples (document_name, clause/section, line_number, relevant_text) for each match found.
    error_handling: If no matches found, return empty list. If multiple documents match, return matches from all; caller must enforce single-source rule.

  - name: enforce_single_source
    description: Validate that answer comes from exactly one document and cite it correctly.
    input: List of search results, user question.
    output: (document_name, clause, line_ref, answer_text) if single-source OR refusal_template if multi-source or no-source.
    error_handling: If results span multiple documents and cannot be answered from one source, return refusal_template. If no results, return refusal_template.
