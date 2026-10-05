skills:
  - name: retrieve_documents
    description: Load and index the three policy documents by section number so the agent can retrieve relevant content from a single source document.
    input: The three policy files: policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: A structured index of sections and text for each document, keyed by document name and section number.
    error_handling: If a required document is missing or unreadable, return a clear error and do not attempt to answer using incomplete data.

  - name: answer_question
    description: Answer an employee question using only the single matching policy document that contains the relevant section, citing the document name and section number for each factual claim.
    input: A user question and the indexed policy documents.
    output: A concise answer grounded in one document only, with citations, or the exact refusal template if no single document covers the question.
    error_handling: If the question cannot be answered from exactly one document, return the exact refusal template instead of blending sources or guessing.
