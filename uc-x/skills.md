# skills.md

skills:
  - name: retrieve_documents
    description: Loads all policy documents and indexes their content by document name and section number to ensure precise retrieval.
    input: List of absolute or relative paths to policy text files.
    output: A structured index (dictionary/object) mapping document names and section IDs to their corresponding text content.
    error_handling: Raises an error if any specified file is inaccessible or if the document structure (sections) cannot be parsed.

  - name: answer_question
    description: Searches the document index to provide a single-source answer with mandatory citation or returns a specific refusal template.
    input: A user query (string) and the structured document index.
    output: A response string containing the answer with source document and section citation, or the exact refusal template if no direct answer exists.
    error_handling: Returns the refusal template verbatim if the answer is not found, requires blending documents, or leads to ambiguous conclusions.
