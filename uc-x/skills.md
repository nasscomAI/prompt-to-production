skills:
  - name: retrieve_documents
    description: Load the company policy documents and index them by document name.
    input: File paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: Dictionary containing document name and full text content.
    error_handling: If any document cannot be loaded, return DOCUMENT_LOAD_ERROR and stop processing.

  - name: answer_question
    description: Answer a user question using only one policy document and include the document name as citation.
    input: User question (string) and indexed policy documents.
    output: Answer referencing a single policy document with its name and section.
    error_handling: If the question is not covered in the documents, return the refusal template exactly as defined.