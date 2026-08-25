skills:
  - name: retrieve_documents
    description: Loads and indexes the three core policy documents (HR, IT, and Finance) to allow for section-specific retrieval.
    input: File paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: A structured index of all policy sections and their verbatim text.
    error_handling: Refuses to start if any of the three mandatory documents are missing or unreadable.

  - name: answer_question
    description: Searches the indexed documents for a single-source answer to a user query, providing citations and strictly avoiding cross-document blending.
    input: A user question (string) and the indexed document set.
    output: A precise answer string citing the document name and section number, OR the standardized refusal template.
    error_handling: Returns the refusal template if the answer is not explicitly found or if answering would require blending claims from multiple documents.
