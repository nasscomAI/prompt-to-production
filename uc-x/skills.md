skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes them by document name and section number.
    input: "Directory or explicit paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt."
    output: "An index dict keyed by (document_filename, section_id) with the full section text."
    error_handling: "If any of the three files is missing, refuse to start Q&A. Do not fill gaps from memory. Wrapped lines stay attached to their section number."

  - name: answer_question
    description: Searches the index and returns a single-source cited answer or the exact refusal template.
    input: "question (string) plus the document index from retrieve_documents."
    output: "A string that is either one cited answer from a single document+section, or the exact refusal template."
    error_handling: "If no section matches, or two documents would both be needed, return the refusal template exactly. Never hedge. Never drop a condition from a matched section."
