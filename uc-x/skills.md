skills:
  - name: retrieve_documents
    description: Loads all 3 required policy files (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt) and indexes them by document name and section number.
    input: None required (uses predefined file paths).
    output: A structured index mapping document names and section numbers to their respective text content.
    error_handling: Raises an error if any of the three required policy documents are missing or unreadable.

  - name: answer_question
    description: Searches the indexed documents and returns a direct, factual single-source answer with document name and section number citation, OR the refusal template.
    input: The user's question as a string, and the indexed policy document data.
    output: A factual answer with source document name and section number citation, OR the exact refusal template.
    error_handling: If the question is not explicitly covered in the documents, or if answering it would require blending sources, it must return exactly: "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."
