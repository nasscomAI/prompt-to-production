skills:
  - name: retrieve_documents
    description: Loads the three policy text files and indexes their numbered sections.
    input: A list of file paths for the policy documents.
    output: A dictionary keyed by file name containing each document title and its section texts.
    error_handling: Raises a FileNotFoundError if a document is missing, or a parsing error if the document sections cannot be indexed.

  - name: answer_question
    description: Searches the indexed policy sections for the best single-source answer to the user's question.
    input: A question string and the indexed policy documents.
    output: A direct answer from a single section with the document title and section citation, or the refusal template if no covered answer exists.
    error_handling: Returns the refusal template if the question is not covered clearly by any single source or if the top matches are ambiguous across documents.
