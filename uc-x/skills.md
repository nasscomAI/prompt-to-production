# skills.md

skills:
  - name: retrieve_documents
    description: Loads all three mandatory policy files and indexes them by document name and section number for precise retrieval.
    input: None (Uses hardcoded paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt).
    output: A structured dictionary/object representing the content of all sections across the documents.
    error_handling: Raises a FileNotFoundError if any of the three documents are missing or unreadable.

  - name: answer_question
    description: Searches the indexed policy documents for a specific answer, ensuring single-source attribution and strict citation.
    input: user_question (string) and indexed_data (object).
    output: A cited answer string formatted as "Answer text [Document Name Section Number]" OR the verbatim refusal template.
    error_handling: Must return the exact refusal template if the information is missing, ambiguous, or requires cross-document blending.
