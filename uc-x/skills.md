skills:
  - name: retrieve_documents
    description: "Load the HR, IT, and Finance policy documents and index them by document name and section number for precise retrieval."
    input: "N/A"
    output: "JSON index containing extracted sections and metadata from policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt."
    error_handling: "If a file is missing or unreadable, the system triggers a fatal error and notifies the administrator."

  - name: answer_question
    description: "Search the indexed documents to provide a single-source answer with metadata or the refusal template."
    input: "User query (string) and the JSON index of documents."
    output: "A combination of specific factual answer + source document name and section number; or the exact refusal template."
    error_handling: "If the question is not explicitly answered in the documents, or if responding would require blending two documents, use the refusal template."
