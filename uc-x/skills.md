# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy text files (HR, IT, and Finance) and parses/indexes them by document name and section number.
    input: Paths to the three policy files.
    output: A dictionary mapping document names and section numbers to the text content.
    error_handling: Handles missing policy files by raising FileNotFoundError.

  - name: answer_question
    description: Searches the indexed document sections and returns a single-source answer with citations, or outputs the refusal template if not found.
    input: User question as string, and indexed documents dictionary.
    output: A text answer citing source document and section, or the standard refusal template.
    error_handling: If there is ambiguity or conflicting information across documents, it refuses to answer and directs the user to the relevant team.
