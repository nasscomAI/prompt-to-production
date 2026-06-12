# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files (HR, IT, Finance) and indexes them by document name and section number.
    input: List of paths to the text files.
    output: A dictionary mapping document names to their content sections.
    error_handling: Raise error if any of the files are missing.

  - name: answer_question
    description: Searches the indexed documents and returns a single-source answer with citations, or the exact refusal template.
    input: The indexed documents and a user's question string.
    output: The answer string.
    error_handling: If the answer requires multiple documents or isn't found, output the strict refusal template.
