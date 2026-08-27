skills:
  - name: retrieve_documents
    description: Loads and indexes all three policy .txt files by document name and section header.
    input: File paths to the HR, IT, and Finance policy documents.
    output: A searchable index of policy clauses and sections.
    error_handling: Refuse to proceed if any of the three mandatory policy files are missing.

  - name: answer_question
    description: Searches the indexed documents to provide a cited answer or the mandatory refusal template.
    input: User's natural language question (string).
    output: A cited answer (String) OR the verbatim refusal template.
    error_handling: If the answer requires blending two different documents, default to the refusal template to prevent scope bleed.
