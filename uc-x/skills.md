skills:
  - name: retrieve_documents
    description: Load and index the three policy documents by document name and section number.
    input: Three policy text files (.txt).
    output: Structured document index with document names and section references.
    error_handling: If a document is missing or unreadable, report the error and do not guess its contents.

  - name: answer_question
    description: Answer a user question using a single policy document with citation or return the refusal template.
    input: User question and indexed policy documents.
    output: Answer with source document name and section number, or the exact refusal template.
    error_handling: If the answer is not present or requires combining multiple documents, return the refusal template exactly without guessing.
