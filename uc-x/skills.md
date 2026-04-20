# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files, parses them into structured sections indexed by document name and section number, enabling precise section-level retrieval for any query.
    input: Directory path or list of file paths to the 3 policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
    output: An indexed collection of sections, each with document_name, section_number, section_heading, and full section text. Returns total section count and document names for verification.
    error_handling: If any of the 3 expected documents is missing, report which document(s) are absent and halt. If a document cannot be parsed into numbered sections, flag it as '[PARSE ERROR - original text preserved]' and include the raw text.

  - name: answer_question
    description: Searches the indexed documents for sections relevant to the user's question, returns a single-source answer with document name and section citation, or the exact refusal template if the question is not covered.
    input: User question (string) and the indexed document collection from retrieve_documents.
    output: Either (a) an answer string with citation in format '[document_name, Section X.X]' sourced from exactly one document, or (b) the exact refusal template if the question is not in any document.
    error_handling: If relevant sections are found in multiple documents, answer from the single most directly relevant section only — never blend. If genuine ambiguity exists between documents, use the refusal template rather than guessing. If hedging language is detected in the generated answer, strip it and re-derive from the source text.
