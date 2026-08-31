# skills.md

skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes their content by document name and section number.
    input: Three policy document file paths in plain-text format.
    output: A structured collection indexed by document filename and numbered policy section.
    error_handling: Reject missing or unreadable documents and never substitute external information.

  - name: answer_question
    description: Searches the indexed policy documents and returns a single-source answer with a section citation or the exact refusal template.
    input: A natural-language policy question and the indexed policy documents.
    output: A factual answer supported by one document and section, or the exact required refusal template.
    error_handling: Refuse questions not covered by the documents and refuse to combine claims from multiple documents.
