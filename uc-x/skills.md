skills:
  - name: retrieve_documents
    description: Loads all three policy .txt files and indexes their content by document name and section number for fast lookup.
    input: List of file paths to the three policy documents.
    output: Dictionary indexed by document name, where each value is an ordered list of sections containing section number and text.
    error_handling: If any of the three files is not found, print an error with the missing file path and exit without answering questions.

  - name: answer_question
    description: Searches the indexed documents for content relevant to the user's question and returns a single-source answer with citation, or the exact refusal template if not found.
    input: User question (string) and the indexed document dictionary from retrieve_documents.
    output: String containing either (a) the answer with citation in format "Source: [document name], Section [X.Y]" or (b) the exact refusal template.
    error_handling: If the question matches content from more than one document and combining them would create a blended answer, use the refusal template rather than risk cross-document contamination.
