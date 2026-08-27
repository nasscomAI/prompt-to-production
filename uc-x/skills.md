# skills.md

skills:
  - name: retrieve_documents
    description: Loads all three policy documents, indexes them by document name and section number, and returns a searchable structure for policy lookup.
    input: A list of policy file paths or the default policy-document directory.
    output: A structured index of sections with document name, section number, and text content.
    error_handling: If a policy file is missing or unreadable, return a clear error and do not continue with answer generation.

  - name: answer_question
    description: Searches the indexed policy documents, returns a single-source answer with citation, or uses the refusal template when the question is not covered.
    input: A user question and the indexed policy-document structure.
    output: A response containing the answer text, the source document and section, or the exact refusal template.
    error_handling: If the answer would require blending multiple documents or if the evidence is ambiguous, return the refusal template rather than guessing.
