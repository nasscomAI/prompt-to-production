skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes their contents by document name and section number.
    input: Three policy .txt files: policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: Indexed policy documents organized by document name and numbered sections.
    error_handling: If a document is missing, unreadable, or cannot be indexed reliably, report the problem and do not invent missing content.

  - name: answer_question
    description: Searches the indexed policy documents and returns a single-source answer with a document and section citation or the exact refusal template.
    input: User question as plain text and the indexed policy documents.
    output: A factual answer supported by one policy document and section citation, or the exact required refusal template when the question is not covered.
    error_handling: If the question is ambiguous, unsupported, or would require combining documents, use the exact refusal template instead of guessing or blending claims.