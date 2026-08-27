# skills.md
skills:
  - name: retrieve_documents
    description: >
      Loads the policy documents and prepares them for search by document
      name and section numbers.
    input: >
      File paths for the three policy documents.
    output: >
      Dictionary structure mapping document name to full text content.
    error_handling: >
      If a document cannot be loaded, stop execution and return an error.

  - name: answer_question
    description: >
      Searches the loaded documents for policy sections that answer
      the user's question and returns the relevant clause with citation.
    input: >
      User question string and the loaded document dataset.
    output: >
      Answer text including document name and section citation.
      If the answer is not present, return the refusal template.
    error_handling: >
      If multiple documents provide conflicting or blended answers,
      refuse rather than combining them.