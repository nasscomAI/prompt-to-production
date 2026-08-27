# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number for precise retrieval.
    input: List of file paths.
    output: Indexed data structure.
    error_handling: Reports error if any file is missing.

  - name: answer_question
    description: Searches indexed documents for relevant information and returns a single-source answer with citation or the standard refusal template.
    input: query (String), indexed_docs (Data structure)
    output: String (Answer + Citation OR Refusal)
    error_handling: Uses the mandatory refusal template if no clear single-source answer exists.
