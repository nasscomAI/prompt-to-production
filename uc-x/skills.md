# skills.md

skills:
  - name: retrieve_documents
    description: Loads the HR, IT, and Finance policy files and indexes them by document name and section number.
    input: None (uses predefined paths for policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt).
    output: Indexed structured data of policy sections.
    error_handling: Logs an error and notifies the user if any of the three policy files are missing or unreadable.

  - name: answer_question
    description: Searches the indexed policy documents to return a single-source answer with a citation or a standardized refusal template.
    input: User's natural language question (String).
    output: A precise answer string with source and section citation, or the verbatim refusal template (String).
    error_handling: If the query is ambiguous or the answer is not found across the three files, it defaults to the refusal template without any hedging.
