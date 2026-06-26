# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    input: List of file paths to the three policy documents (list of strings)
    output: A structured dictionary mapping document names and section numbers to their text content.
    error_handling: Raise an error if any of the three required documents cannot be read or parsed.

  - name: answer_question
    description: Searches the indexed documents and returns a clean, single-source answer with a citation, or returns the exact refusal template if the answer is missing or ambiguous across documents.
    input: The indexed document dictionary (from retrieve_documents) and the user's question (string)
    output: A formatted response string containing either the cited answer or the verbatim refusal template.
    error_handling: Automatically trigger the strict refusal template if multiple documents conflict or if no single section provides a definitive answer. Do not attempt to hedge or synthesize a partial answer.
