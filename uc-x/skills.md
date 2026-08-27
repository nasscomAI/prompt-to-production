skills:
  - name: retrieve_documents
    description: Load the three policy files and index their numbered sections by document name.
    input: Paths to the HR, IT, and Finance policy text files.
    output: A searchable mapping of document names to section-numbered text.
    error_handling: If a document cannot be loaded or parsed into sections, stop and report that document name.

  - name: answer_question
    description: Answer a policy question from one source document with a citation or return the refusal template.
    input: A user question and the indexed policy documents.
    output: A single-source answer with document and section citation, or the exact refusal template.
    error_handling: If no document contains a supported answer or the answer would require blending, return the refusal template exactly.
