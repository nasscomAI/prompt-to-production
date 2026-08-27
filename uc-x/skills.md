# skills.md

skills:

  - name: retrieve_documents
    description: Loads all three policy files and indexes their content by document name and section number.
    input: Directory containing the three policy text files.
    output: Indexed policy documents organized by document name and section number.
    error_handling: Report an error when no policy documents are available and do not invent missing content.

  - name: answer_question
    description: Searches the indexed policies and returns a single-source answer with citation or the exact refusal template.
    input: Indexed policy documents and a natural-language policy question.
    output: One answer supported by one document and section, or the exact refusal template.
    error_handling: Refuse questions not covered by the documents and never combine information from multiple documents.