# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy documents and indexes their content by document name and section number.
    input: None
    output: A structured index of policy text and section headers.
    error_handling: System reports error if any of the mandatory files are missing.

  - name: answer_question
    description: Searches the doc index to return a single-source answer with citations or the refusal template.
    input: User natural language search query.
    output: String (Formatted answer with citation or refusal text).
    error_handling: If no single source provides a clear answer, triggers the verbatim refusal template.
