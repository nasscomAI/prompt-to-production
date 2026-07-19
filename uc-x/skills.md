skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes their content by document name and section number.
    input:
      type: list
      format: A list of file paths pointing to the three policy .txt documents.
    output:
      type: dict
      format: A nested dictionary mapping document names to a dict of section numbers to clause text strings.
    error_handling:
      rules:
        - "If any file is not found, raise FileNotFoundError with the missing file path."
        - "If a file is empty, log a warning and continue with the others."

  - name: answer_question
    description: Searches the indexed documents for the best matching section and returns a single-source, citation-backed answer — or the exact refusal template if nothing is found.
    input:
      type: dict
      format: A dictionary with 'question' (string) and 'index' (the document index from retrieve_documents).
    output:
      type: str
      format: A human-readable answer string with document name and section citation, or the verbatim refusal template.
    error_handling:
      rules:
        - "If the question matches content in more than one document and combining them would form a blended answer, refuse rather than blend."
        - "If no matching content is found in any document, output the exact refusal template verbatim."
        - "Never output hedging phrases like 'while not explicitly covered' or 'typically'."
