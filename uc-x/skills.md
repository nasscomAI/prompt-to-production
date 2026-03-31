# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes their contents accurately by document name and section number.
    input: List of file paths to the 3 distinct policy text documents.
    output: A structured index mapping document names and section numbers to their exact text content.
    error_handling: System exits or flags an error if any of the required policy files is missing or unreadable.

  - name: answer_question
    description: Searches indexed documents for the specific policy clause addressing the user's question, strictly returning a single-source answer with citation, or the refusal template.
    input: User's question string and the structured document index.
    output: A string containing the exact factual answer with document and section citation, or the exact refusal template.
    error_handling: If the question overlaps ambiguously across documents or isn't covered, strictly outputs the predefined refusal template without variation.
