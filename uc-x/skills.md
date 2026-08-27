skills:
  - name: retrieve_documents
    description: Loads all policy documents and organizes them by document name and section for structured access.
    input: List of file paths to policy text documents
    output: Dictionary mapping document names to their contents as lists of lines (section-wise text)
    error_handling: Raises error if any file is missing, unreadable, or empty

  - name: answer_question
    description: Searches the documents for a relevant answer and returns a single-source response with document and section citation or the refusal template.
    input: Dictionary of documents and user question (string)
    output: Answer string with document name and section reference OR refusal template
    error_handling: 
      - If no relevant answer is found, return the refusal template exactly  
      - If answer spans multiple documents, refuse instead of combining  
      - If question is ambiguous or cannot be matched clearly to one section, return refusal template