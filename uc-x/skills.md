skills:
  - name: retrieve_documents
    description: Loads the three policy files and indexes them by document name and section number.
    input: Paths to the available policy text files.
    output: A structured document index mapping document names and section numbers to clause text.
    error_handling: If a file cannot be read, return an error and do not answer from that file.

  - name: answer_question
    description: Returns a single-source policy answer with citation or the exact refusal template.
    input: A natural-language question and the indexed policy documents.
    output: A grounded answer with document name and section number, or the refusal template.
    error_handling: If no exact support is found or multiple documents create ambiguity, return the refusal template.