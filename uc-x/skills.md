# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    input: No input parameters required.
    output: A collection of indexed document sections with document name, section number, and text.
    error_handling: Return an error message indicating if a file fails to load or parse.

  - name: answer_question
    description: Searches indexed documents and returns a single-source answer with citation OR the refusal template.
    input: User question text (string) and the retrieved indexed documents.
    output: A response strictly formatted with the answer and citation, or the exact refusal template.
    error_handling: If the answer requires blending documents or isn't found, return the exact refusal template.
