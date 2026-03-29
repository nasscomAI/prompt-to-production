# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files from the specified directory, parses them into sections indexed by document name and section number.
    input: Directory path string containing the policy files.
    output: Dictionary with document names as keys, each value being a dictionary of section numbers to section text.
    error_handling: If a file is not found, use an empty string for that document and continue with others.

  - name: answer_question
    description: Searches the indexed documents for a relevant section based on the question, returns the section text with citation if found from a single document, otherwise returns the refusal template.
    input: Question string and the documents dictionary from retrieve_documents.
    output: Answer string either with source citation and text or the refusal message.
    error_handling: If the question matches sections in multiple documents or no documents, return the refusal template.
