skills:
  - name: retrieve_documents
    description: Loads all three policy files (HR, IT, Finance) and indexes their contents accurately by document name and section number.
    input: A list of file paths to the policy documents.
    output: A structured index (e.g., nested dictionary) mapping document names and section numbers to their exact text.
    error_handling: Raises a FileNotFoundError if any document is missing or cannot be read.

  - name: answer_question
    description: Searches the indexed documents to provide a strict, single-source answer to a user's question, including exact citations.
    input: The structured document index and the user's question (string).
    output: A string containing the direct answer and its specific citation (Document Name, Section), OR the exact refusal template.
    error_handling: If the answer requires blending information from multiple documents, or if the question is not covered, it strictly outputs the exact refusal template with no variations. It must never output hedging phrases.
