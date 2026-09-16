skills:
  - name: retrieve_documents
    description: Load and index all three policy documents by document name and section number.
    input: A configured set of paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: An index containing each document's text, document name, and section-numbered content.
    error_handling: Report missing or unreadable files and do not create an incomplete index.

  - name: answer_question
    description: Search the indexed policy documents and answer from one source document or return the exact refusal template.
    input: A user's policy question and the index produced by retrieve_documents.
    output: A concise answer supported by one policy document with its document name and section number, or the exact refusal template when the question is not covered.
    error_handling: Refuse rather than guess when the question is not covered or when answering would require blending claims from multiple documents.
