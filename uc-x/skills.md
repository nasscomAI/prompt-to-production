skills:
  - name: Document Loading
    description: Reads a policy document from the policy-documents directory.
    input: File path (string)
    output: List of text lines from the document
    error_handling: Returns an empty list if the document cannot be opened.

  - name: Query Matching
    description: Searches the document text to find lines relevant to the user query.
    input: Query string and list of document lines
    output: Matching lines that contain relevant information
    error_handling: Returns no matches if the query cannot be found.

  - name: Answer Generation
    description: Generates a response based only on the matched document text.
    input: Matching document lines
    output: Answer string derived from the document
    error_handling: Returns a refusal message if no supporting text exists.