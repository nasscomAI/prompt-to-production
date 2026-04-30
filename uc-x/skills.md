skills:
  - name: [retrieve_documents]
    description:[Loads all 3 policy files and indexes them by document name and section number.]
    input:
      [type: array
      format: List of filepaths to the 3 policy text files]
    output:
      [type: object
      format: Indexed dictionary mapping document names and section numbers to their text content
    error_handling: Throws an error if any of the required policy files are missing or inaccessible.]

  - name: [answer_question]
    description: [Searches the indexed documents to return a single-source answer with a citation or the exact refusal template.]
    input:
      [type: string
      format: User's question text]
    output:
      [type: string
      format: Answer text with document/section citation, or the exact refusal template]
    error_handling: [Returns the exact refusal template if the answer requires cross-document blending, condition dropping, or is not found.]
    
