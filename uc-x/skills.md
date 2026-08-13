# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: >
      Loads all three policy files and indexes them by document name and section
      number so every claim can be traced to a source.
    input: >
      list of str — paths to policy_hr_leave.txt, policy_it_acceptable_use.txt,
      policy_finance_reimbursement.txt.
    output: >
      dict — index of {document_name: {section_number: section_text}} plus document
      metadata (reference, version).
    error_handling: >
      Raises a clear error if a document is missing or unreadable; preserves section
      numbers exactly as written so citations are always accurate.

  - name: answer_question
    description: >
      Searches the indexed documents and returns a single-source answer with citation,
      or the exact refusal template when the question is not covered.
    input: >
      question (str) + the index produced by retrieve_documents.
    output: >
      str — either "Answer (Source: document_name, section X.Y)" with every claim
      cited from ONE document, or the exact refusal template.
    error_handling: >
      If the question's answer would require combining two documents, returns the
      refusal template instead of blending. If no section matches, returns the refusal
      template verbatim — never hedges, never invents policy.