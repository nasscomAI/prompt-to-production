# skills.md — UC-X Document Q&A Skills

skills:
  - name: retrieve_documents
    description: Loads and indexes policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt) by document name and section number.
    input: Directory path containing policy text files.
    output: Data structure containing parsed sections indexed by document name and section number.
    error_handling: Raises FileNotFoundError if any policy document is missing from the designated directory.

  - name: answer_question
    description: Answers a user query using a single source document with exact citations, or returns the refusal template if ungrounded or ambiguous across documents.
    input: Query string and indexed policy documents.
    output: String containing single-source answer with document name and section citation, or exact refusal template.
    error_handling: Returns exact refusal template if question is ungrounded or if multi-document blending would occur.
