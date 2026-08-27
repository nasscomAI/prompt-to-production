# skills.md

skills:
  - name: retrieve_documents
    description: Simultaneously loads and indexes all policy documents (HR, IT, Finance) by document name and section number for rapid lookups.
    input: Directory path containing the .txt policy documents.
    output: A structured index where keys are document names and section IDs.
    error_handling: Notifies the user if any of the three critical policy files are missing.

  - name: answer_question
    description: Processes a user query by searching the indexed documents. Returns high-fidelity answers with citations or triggers the refusal template.
    input: User string query and the document index.
    output: A single-document answer with citation (Doc name + Section) OR the verbatim refusal template.
    error_handling: If a question is partially covered in two documents, it prioritizes the most specific one or refuses to avoid blending.
