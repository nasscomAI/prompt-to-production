skills:
  - name: retrieve_documents
    description: Loads the three official company policy files and indexes their text contents by document filename and section number.
    input: File paths to the three policy documents as strings or a list of filepaths.
    output: A structured index mapping each document filename and section number to its policy text.
    error_handling: If any required policy file is missing, unreadable, or malformed, raise a file loading error and stop execution rather than operating on incomplete policy context.

  - name: answer_question
    description: Searches the indexed policy documents to provide a concise, single-source factual answer with citations or returns the exact refusal template.
    input: An employee's natural language question as a string and the indexed documents produced by retrieve_documents.
    output: A string containing a factual answer supported by one policy document with the document filename and section number cited for every factual claim, OR the exact refusal template.
    error_handling: If ambiguity arises or if the question is not covered, refuse only when the question cannot be answered clearly from a single available policy document, returning the exact refusal template without guessing, hedging, or combining claims from multiple documents.
