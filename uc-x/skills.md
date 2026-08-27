skills:
  - name: retrieve_documents
    description: Loads the HR, IT, and Finance policy files and indexes each numbered section by document and section number.
    input: Directory path containing policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: Dictionary keyed by source document name and section number.
    error_handling: Raise a clear error if any required document is missing or unreadable.

  - name: answer_question
    description: Answers a policy question from a single source document with citations or returns the exact refusal template.
    input: User question string and indexed policy documents.
    output: One answer string with source file and section citations, or the exact refusal template.
    error_handling: Refuse questions that are unsupported, ambiguous across documents, or require blending multiple policies.
