skills:
  - name: retrieve_documents
    description: Loads and indexes all 3 municipal policy text files, organizing content into searchable section records tagged by document name and section number.
    input: List of string file paths to policy files (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
    output: Structured index dictionary mapping document names and section IDs to section text and clause definitions.
    error_handling: Raises FileNotFoundError if any policy file is missing; logs indexing warnings for unformatted headers.

  - name: answer_question
    description: Evaluates a user policy query against the indexed document store, returning a single-source cited answer or triggering the verbatim refusal template.
    input: String question query and structured document index from retrieve_documents.
    output: Formatted response string containing document and section citations OR the exact refusal template string.
    rule_enforcement:
      single_source: Prevents cross-document blending by selecting the authoritative single source.
      no_hedging: Rejects answers containing 'typically', 'generally', or 'while not explicitly covered'.
      refusal_template: Emits exact refusal text when no document contains authoritative text for the query.
    error_handling: Rejects ambiguous multi-doc blends and defaults to the standard refusal template.
