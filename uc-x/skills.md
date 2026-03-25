# skills.md

skills:
  - name: retrieve_documents
    description: Loads all policy files from the data directory and indexes them by filename and clause number.
    input: File path list.
    output: Indexed collection of policy text sections.
    error_handling: Return error if files are missing or inaccessible.

  - name: answer_question
    description: Searches the indexed policy documents for relevant clauses and returns a single-source response with citations.
    input: User question and indexed policy data.
    output: Structured response text containing the fact and [Document, Section] citation, or the refusal template.
    error_handling: Trigger refusal template if more than one source document suggests conflicting or broad conclusions.
