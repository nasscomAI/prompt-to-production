# skills.md

skills:
  - name: retrieve_documents
    description: Loads and indexes all policy files by document name and section number for precise searching.
    input: The file paths for the HR, IT, and Finance policy documents.
    output: A data structure representing the indexed sections of each policy document.
    error_handling: Logs an error if any of the three documents are missing or fail to load.

  - name: answer_question
    description: Searches the indexed documents and returns a factual answer + citation OR the refusal template.
    input: An input query (as string) and the indexed policy documents.
    output: A single-source answer with document name and section number citations.
    error_handling: Returns the refusal template if the answer cannot be found in the documents or involves document blending.
