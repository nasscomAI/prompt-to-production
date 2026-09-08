# skills.md

skills:
  - name: retrieve_documents
    description: Load all three policy documents and index them by document name and section number for answer retrieval.
    input: A directory containing policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: A structured index mapping each document name and section number to its source text, so the answerer can cite the correct document and section.
    error_handling: If a document is missing or unreadable, return a document-access error and refuse to answer instead of using an unverified section.

  - name: answer_question
    description: Search the indexed policy documents, return a precise answer from one document section only, or issue the required refusal template when the question is not covered.
    input: A natural-language question string and the indexed policy document structure from retrieve_documents.
    output: A natural-language answer citing the document name and section number, or the exact refusal template if the question is outside the available documents.
    error_handling: If the question raises a multi-document ambiguity or a cross-document blend risk, refuse to combine sources and answer only from the one document that directly supports the question, or return the defined refusal template exactly.
