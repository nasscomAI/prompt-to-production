skills:
  - name: retrieve_documents
    description: Loads the three policy TXT files and indexes their content by document name and section number.
    input: List of file paths (strings).
    output: A dictionary structure where keys are document names and values are sub-dictionaries of sections.
    error_handling: Raise FileNotFoundError if any source file is missing.

  - name: answer_question
    description: Searches the indexed documents to find a single-source answer with citations.
    input: User question (string) and indexed documents (dictionary).
    output: A string containing the answer with citation (Doc Name + Section) OR the mandated refusal template.
    error_handling: Use the exact refusal template if the answer involves cross-document blending, hedging, or is not in the source documents.
