skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    input: A list of file paths to the policy documents.
    output: A dictionary where keys are document names and values are dictionaries mapping section numbers to text.
    error_handling: If a file cannot be read, log a warning and continue with the others. Return whatever could be successfully parsed.

  - name: answer_question
    description: Searches the indexed documents and returns a single-source answer with citation, or a strict refusal template.
    input: A string representing the user's question, and the indexed documents dictionary.
    output: A string containing either the answer with citation or the exact refusal template.
    error_handling: If the answer requires blending documents or uses hedging language, or if the question is simply not found, return the exact refusal template without variation.
