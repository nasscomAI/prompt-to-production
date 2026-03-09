# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy text files and indexes them by document name and section number.
    input: None or list of file paths (list of strings).
    output: A nested dictionary structure mapping document names to section numbers and text.
    error_handling: Raise an error if any of the required policy files is missing.

  - name: answer_question
    description: Searches the indexed documents and returns a single-source answer with a strict citation, or the exact refusal template if the answer is missing or ambiguous.
    input: question (string), indexed_documents (dict).
    output: Answer string with citation (string).
    error_handling: If a question requires blending across multiple documents or the answer is not explicitly covered, return the exact refusal template immediately.
