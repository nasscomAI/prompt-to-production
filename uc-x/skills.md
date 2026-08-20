# skills.md

skills:
  - name: retrieve_documents
    description: Load all three policy files and organize their content by document name and section number.
    input: Three policy file paths as strings.
    output: Structured policy sections indexed by document name and section number.
    error_handling: If a file cannot be read, report the error and do not invent or replace its content.

  - name: answer_question
    description: Answer a policy question using claims from one source document only, with a document and section citation.
    input: A user question and the indexed policy documents.
    output: A single-source answer with document name and section number, or the exact refusal template when the question is not covered.
    error_handling: Never guess, blend documents, hedge, or drop conditions; use the exact refusal template when the answer is not supported.
