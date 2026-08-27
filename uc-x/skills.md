# skills.md

skills:
  - name: retrieve_documents
    description: Loads and indexes the HR, IT, and Finance policy documents by document name and section number.
    input: None (internal paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt).
    output: Indexed collection of document sections with metadata.
    error_handling: Logs an error and terminates if any of the three mandatory files are missing or unreadable.

  - name: answer_question
    description: Searches the indexed policy documents to provide a single-source answer with citations or the mandatory refusal template.
    input: User question (String).
    output: String containing the verified answer + citation (Document Name + Section) OR the exact refusal template.
    error_handling: Returns the refusal template if the question is ambiguous or if the information is spread across multiple documents without a clear single source.
