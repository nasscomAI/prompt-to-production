# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Load all 3 policy files and index them by document name and section number.
    input: Directory or explicit paths of policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt.
    output: Index of {doc, section, text} preserving original wording, numbers, AND/OR conditions and limits; missing file raises an error naming it.
    error_handling: FileNotFoundError with path if any document is missing; empty/unparseable file yields no sections rather than invented ones; never substitutes outside knowledge.

  - name: answer_question
    description: Search the index and return a single-source cited answer or the exact refusal template.
    input: User question string plus the document index from retrieve_documents.
    output: Either one answer citing exactly one document filename + section number(s) from that document only, or the exact refusal template verbatim when uncovered or cross-document.
    error_handling: Zero matching sections returns the refusal template; matches spanning two documents returns the refusal template instead of blending; never emits hedging phrases (typically, generally, while not explicitly covered).
