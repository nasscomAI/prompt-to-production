# skills.md

skills:
  - name: retrieve_documents
    description: Loads the HR, IT, and Finance policy files and indexes them by document name and section number.
    input: all three policy files (e.g., '../data/policy-documents/)
    output: Indexed collection of document sections in JSON format.
    error_handling: Logs a critical error and fails to initialize if any required policy file is missing.

  - name: answer_question
    description: Searches the indexed policy documents to provide a single-source answer with a citation or the exact refusal template.
    input: User question as a string.
    output: A single-source answer with citation (Doc name + Section) or the verbatim refusal template as a string.
    error_handling: Returns the refusal template if no answer is found or if the answer would require blending multiple sources.
