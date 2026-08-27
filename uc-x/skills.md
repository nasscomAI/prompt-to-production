skills:
  - name: retrieve_documents
    description: Loads the three official CMC policy documents and parses them into a searchable index organized by document name and section number.
    input: None (uses predefined paths to the three policy files).
    output: A structured index of policy sections and their contents.
    error_handling: Reports an error if any of the three mandatory policy files are missing or unreadable.

  - name: answer_question
    description: Searches the policy index for information relevant to a user's question and provides a single-source answer with a citation.
    input: User question as a string.
    output: A string containing the answer and citation, or the mandatory refusal template if no answer is found.
    error_handling: Strictly refuses to blend documents or provide hedged answers; defaults to the refusal template for any ambiguity.
