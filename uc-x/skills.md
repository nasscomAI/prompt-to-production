# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Load all three policy files and index them by document name and section number.
    input: Paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: An index mapping each document name to its parsed sections and numbered clauses.
    error_handling: If any of the three files cannot be read, report the missing file and refuse to answer until all documents are loaded.

  - name: answer_question
    description: Search the indexed documents and return a single-source answer with citation, or the refusal template if not covered.
    input: A free-text policy question and the indexed documents from retrieve_documents.
    output: A concise answer citing the source document name and section number, or the exact refusal template when the question is not covered.
    error_handling: If an answer would require combining claims from two different documents, return the single relevant source or refuse with the template; never hedge or invent.
