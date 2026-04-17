skills:
  - name: retrieve_documents
    description: Loads all three policy files (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt) and indexes their contents accurately by document name and section number.
    input: File paths to the three required policy documents.
    output: A structured index mapping document names and section numbers to their respective textual content.
    error_handling: Fail gracefully if any of the three documents are missing or unreadable. Ensure section boundaries are parsed accurately without dropping content.

  - name: answer_question
    description: Searches the indexed documents for an answer to the user's question. It must strictly adhere to single-source constraints and refusal templates without any cross-document blending.
    input: The user's question and the indexed document context from retrieve_documents.
    output: A single-source answer that explicitly cites the document name and section number, OR the exact verbatim refusal template if the answer is not fully covered.
    error_handling: If a question requires blending information from multiple documents, or if the answer is not explicitly present, immediately return the required refusal template. Do not attempt to guess or hedge.
