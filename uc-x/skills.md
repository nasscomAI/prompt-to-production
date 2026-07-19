skills:
  - name: retrieve_documents
    description: Load all policy text files and organize the content by document name and section header.
    input: None.
    output: Dictionary representing the indexed policy sections.
    error_handling: Log errors if any policy document is missing or cannot be read.

  - name: answer_question
    description: Match user questions against the policy index, returning a single-source cited answer or the exact refusal template.
    input: Question string.
    output: Answer string with document and section citations, or the exact refusal template.
    error_handling: Return the exact refusal template if the answer is not clearly present in a single source.
