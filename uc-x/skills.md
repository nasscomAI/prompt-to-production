# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files, indexes by document name and section number.
    input: List of file paths to the policy documents.
    output: Indexed collection of document content, organized by name and section.
    error_handling: Return error if files are missing or inaccessible.

  - name: answer_question
    description: Searches indexed documents and returns a single-source answer with citation or the refusal template.
    input: User question (string) and indexed documents.
    output: Formatted answer string with citation or refusal message.
    error_handling: Return refusal template if the question is ambiguous or not found in documents.
