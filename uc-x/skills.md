# skills.md

skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes them by document name and section number.
    input: Paths to the three policy .txt files.
    output: A structured index (dictionary) where keys are document names and values are lists of sections.
    error_handling: If any file is missing, reports the missing file and loads the remaining ones.

  - name: answer_question
    description: Searches the indexed documents for the answer to a user question and returns a cited answer or the refusal template.
    input: User question and the indexed documents.
    output: A string containing the answer with citations [Document, Section] or the exact refusal template.
    error_handling: If the answer requires blending documents or is not found, it triggers the refusal template.
