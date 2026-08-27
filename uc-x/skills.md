skills:
  - name: retrieve_documents
    description: Loads and indexes policy documents by document name and section number.
    input: >
      File paths (list of strings) pointing to policy text files
    output: >
      Structured document store (dictionary) with:
      {document_name: {section_number: section_text}}
    error_handling: >
      If file not found → raise error;
      If file unreadable → raise error;
      If sections cannot be parsed → return partial structure with warning.

  - name: answer_question
    description: Searches documents and returns a single-source answer with citation or refusal.
    input: >
      User question (string) + indexed documents (dictionary)
    output: >
      Either:
      - Answer string with document name + section citation
      OR
      - Refusal template (exact match, no variation)
    error_handling: >
      If no relevant section found → return refusal template;
      If multiple documents contain partial answers → refuse (no blending allowed);
      If ambiguous query → prefer refusal over assumption.