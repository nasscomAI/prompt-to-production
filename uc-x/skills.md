# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files (HR leave, IT acceptable use, Finance reimbursement), indexes them by document name and section number for search.
    input: Directory path containing the three policy .txt files.
    output: A structured index mapping document_name -> section_number -> clause_text for all three policy documents.
    error_handling: If any policy file is missing or unreadable, reports the error and continues with available files. Never fabricates content for missing files.

  - name: answer_question
    description: Searches the indexed documents for the answer to a user question, returns a single-source cited answer or the exact refusal template.
    input: A user question (str) and the document index from retrieve_documents.
    output: Either (a) an answer citing exactly one document name and section number per factual claim, or (b) the refusal template with the appropriate team name.
    error_handling: If the question matches content in multiple documents, answers from only one document (the most specific match). If no document covers the question, returns the refusal template. Never hedges, blends, or infers.
