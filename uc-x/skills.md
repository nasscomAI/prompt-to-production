# skills.md

skills:
  - name: retrieve_documents
    description: Loads all policy documents and indexes them by document name and section number.
    input: A list of policy text file paths.
    output: A dictionary mapping document names to section-indexed text.
    error_handling: If a file is missing, stop and report the missing document instead of answering from incomplete information.

  - name: answer_question
    description: Searches the indexed policy documents and returns a single-source answer or the required refusal template.
    input: A user question string and the indexed policy documents.
    output: A concise answer with a document citation or the exact refusal template.
    error_handling: If the answer is uncertain or spans multiple documents, return the refusal template rather than guessing.
