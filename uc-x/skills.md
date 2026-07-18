skills:
  - name: retrieve_documents
    description: Loads the three policy text files and parses/indexes them by document name and section/clause number for precise retrieval.
    input: Paths to the three policy files (list of strings).
    output: An indexed data structure containing text segments mapped to document names and clause numbers.
    error_handling: Raises an error if any of the files cannot be loaded.

  - name: answer_question
    description: Searches the indexed document sections to answer a user's question, applying strict single-source citation rules, and returning the exact refusal template if no direct answer exists.
    input: User's question (string) and the indexed documents structure.
    output: A string containing either the cited answer or the exact refusal template.
    error_handling: If a question is partially covered or creates ambiguity across documents, it returns the exact refusal template.
