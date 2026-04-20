# skills.md

skills:
  - name: retrieve_documents
    description: Loads all policy files and organizes the content by document name and section number for quick lookup.
    input: List of paths to policy text files.
    output: A structured index of sections across all documents.
    error_handling: Logs any files that are missing or cannot be parsed.

  - name: answer_question
    description: Searches the indexed documents for an answer to a specific question, ensuring a single-source response or a strict refusal.
    input: User's question and the indexed documents.
    output: A string containing the answer with citation, or the exact refusal template.
    error_handling: If multiple documents contain conflicting or partial info that would lead to blending, returns a refusal.
