skills:
  - name: retrieve_documents
    description: Loads all 3 policy text files (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt) and indexes sections and clauses by document name and section number.
    input: Directory path to policy documents (string).
    output: Structured dictionary mapping document names and section/clause identifiers to text content.
    error_handling: Raises FileNotFoundError if any of the three policy files cannot be found.

  - name: answer_question
    description: Matches user query against indexed policy clauses, enforces single-document attribution, appends document and section citations, or outputs verbatim refusal template.
    input: User question (string) and indexed policy document database.
    output: Plain text response containing accurate clause answer + citation OR verbatim refusal text.
    error_handling: Outputs refusal template if no matching policy clause is found or if query requires cross-document speculation.
