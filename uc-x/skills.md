# Skills

skills:
  - name: retrieve_documents
    description: Load the three policy documents and index them by section number.
    input: Paths to the three policy text files.
    output: Indexed document sections keyed by document and section number.
    error_handling: Raise an error if a document cannot be opened or parsed.

  - name: answer_question
    description: Search indexed documents for a single-source answer or return the refusal template.
    input: A question string plus the indexed policy documents.
    output: A single answer string with citation or the exact refusal template.
    error_handling: Return the exact refusal template when the question is not covered.
