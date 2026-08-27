skills:
  - name: retrieve_documents
    description: Loads the three policy documents and indexes their content by document name and section number.
    input: "list of policy file paths (.txt): HR leave, IT acceptable use, and finance reimbursement."
    output: "searchable index keyed by document name and section number with exact source text spans."
    error_handling: "If any required file is missing or unparseable, return a retrieval error listing affected files and block answering until corpus is complete."

  - name: answer_question
    description: Answers a policy question using one document section with citation, or returns the exact refusal template when not covered.
    input: "user question string + indexed policy corpus from retrieve_documents."
    output: "single-source answer with document+section citation, or exact refusal template if unsupported by source text."
    error_handling: "If evidence is missing, conflicting across documents, or requires blending to answer, do not infer; return the exact refusal template."
