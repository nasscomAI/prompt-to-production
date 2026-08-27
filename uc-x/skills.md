skills:
  - name: retrieve_documents
    description: Loads the three required policy files and strictly indexes them by document name and section number to enable exact citations.
    input: A list of absolute file paths to the three policy text files.
    output: A structured index or dictionary mapping document names and specific section numbers to their exact text.
    error_handling: If any document is missing or cannot be clearly parsed into numbered sections, raise an error and refuse to initialize the agent.

  - name: answer_question
    description: Searches the indexed policy documents to provide a strictly single-source answer with explicit citation, or falls back to the exact refusal template.
    input: A user's natural language question and the structured document index.
    output: A string containing the answer with document and section citation, or the exact refusal template.
    error_handling: If the answer requires blending multiple documents or the information is missing, immediately return the exact refusal template. Do not attempt to guess, interpolate, or hedge.
