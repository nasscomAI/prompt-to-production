skills:
  - name: retrieve_documents
    description: Loads all 3 policy text files and indexes them by document name and section number.
    input: List of file paths to the policy documents (HR, IT, Finance).
    output: A structured dictionary or index mapping each section number to its specific document name and text content.
    error_handling: Raises an error if any of the required policy files exist but cannot be read or are missing.

  - name: answer_question
    description: Searches the indexed documents and returns a single-source answer with a citation, or explicitly refuses to answer.
    input: The user's specific question (string) and the retrieved document index.
    output: A response string containing the exact factual answer with the source doc and section number cited, or the verbatim refusal template.
    error_handling: Uses the exact refusal template ("This question is not covered in the available policy documents...") if the answer cannot be cleanly derived from a single document without hallucination or blending.
