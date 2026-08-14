# skills.md — UC-X Skills

skills:
  - name: retrieve_documents
    description: Loads and indexes policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt, parsing each into numbered sections and verbatim clause text.
    input: Base directory path to policy documents.
    output: A dictionary keyed by document name, each value with header and sections containing exact clause numbers and text.
    error_handling: Raises FileNotFoundError naming the missing file; reads UTF-8 safely; keeps every clause's text verbatim so answers never add or reword content.

  - name: answer_question
    description: Matches a question to indexed clauses and returns a single-source answer that quotes the exact clause text and cites the document name plus section numbers, or returns the verbatim refusal template when the topic is not covered.
    input: Question string.
    output: A single-document answer with document name and section-number citation built from verbatim clause text, or the exact refusal template (no variations, no hedging).
    error_handling: Never blends claims from two different documents; never uses hedging phrases; refuses cleanly when a question is out of scope or when no single document clearly matches; refuses when the required documents are missing.
