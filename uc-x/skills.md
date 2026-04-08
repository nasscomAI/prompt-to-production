skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    input: File paths to the 3 company policy documents.
    output: A structured index or mapping of Document Name and Section Number to its exact text content.
    error_handling: Raise an error if any of the three documents cannot be loaded or if section numbers cannot be extracted.

  - name: answer_question
    description: Searches the indexed documents and returns a single-source answer with citation, OR the refusal template.
    input: The user's question and the indexed document context.
    output: A string containing either the factual answer with source document name and section number, or the exact refusal template.
    error_handling: Return the exact refusal template if the answer requires blending two or more documents, or if the question is not explicitly covered in any single document.
