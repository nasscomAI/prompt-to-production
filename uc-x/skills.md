# skills.md

skills:
  - name: retrieve_documents
    description: Loads and indexes the content of HR, IT, and Finance policy files by section number.
    input: List of paths to the policy `.txt` files.
    output: A structured index mapping document names and section IDs to their corresponding text.
    error_handling: Raises an error if any of the three core policy files are missing or unreadable.

  - name: answer_question
    description: Searches the indexed documents for keywords matching the user query and formats a cited response or refusal.
    input: User question string and the indexed document structure.
    output: A string containing the answer with citations or the mandatory refusal template.
    error_handling: Defaults to the refusal template if no single source can confidently answer the question.
