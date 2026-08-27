skills:
  - name: retrieve_documents
    description: Loads all 3 policy files (HR, IT, Finance) and indexes them by document name and section number.
    input: None required (uses predefined paths to the three policy txt files).
    output: An indexed dictionary mapping each document and section number to its verbatim text content.
    error_handling: Raises an error if any of the three policy files are missing or cannot be read.

  - name: answer_question
    description: Searches the indexed documents to answer a user question using a single source, strictly citing the document name and section number.
    input: The user's question as a string, and the indexed documents object.
    output: A precise answer string accompanied by its source citation (Document + Section), or the exact formatted refusal template if the answer is missing or requires cross-document blending.
    error_handling: Immediately returns the exact refusal template if the answer cannot be found in a single section without blending or assumptions.
