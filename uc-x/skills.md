skills:
  - name: retrieve_documents
    description: Loads a designated set of policy text files and parses them into an indexed collection mapped by document name and section numbers.
    input: An array/list of file path strings pointing to the required policy documents.
    output: A single searchable knowledge index containing the structured contents of all loaded documents.
    error_handling: Raise an invalid format error if an essential file is missing, empty, or unreadable.

  - name: answer_question
    description: Processes a user's natural language question against the retrieved documents and returns a properly cited answer or a templated refusal string.
    input: A string containing the user's question, and a reference to the loaded document index array.
    output: A text answer string derived strictly from one specific section of one document containing the mandatory citation, or the exact refusal template string.
    error_handling: Return the designated exact refusal template string if the question cannot be answered cleanly from a single document source.
