skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes their text content by document name and section/clause number.
    input: List of paths to the three policy files (strings).
    output: A structured dictionary indexing section/clause texts by document name and section/clause number.
    error_handling: If any of the files are missing or unreadable, it raises a FileNotFoundError or ValueError.

  - name: answer_question
    description: Searches the indexed policy sections to find a single-source answer to the user's question, including a citation or returning the refusal template.
    input: User's question (string) and the indexed policy sections dictionary.
    output: An answer string citing the source document and section number, or the exact refusal template if not found.
    error_handling: Refuses to blend information from multiple documents or use hedging language. Returns the exact verbatim refusal template if the answer is missing, ambiguous, or not covered.

