skills:

* name: retrieve_documents
  description: "Loads and indexes all provided policy documents by document name and section number for structured retrieval."
  input: "List of file path strings to policy .txt documents."
  output: "A structured index mapping document names to their numbered sections and corresponding text content."
  error_handling: "If any file path is invalid or unreadable, abort with an error; if documents lack identifiable section numbering, abort; if any document is missing, do not proceed to prevent incomplete retrieval."

* name: answer_question
  description: "Searches the indexed documents and returns a single-source answer with citation or the exact refusal template if not found."
  input: "User question string and structured indexed documents."
  output: "A string containing either a precise answer with document name and section citation or the exact refusal template."
  error_handling: "If the question maps to multiple documents without a complete answer in any one, refuse using the template; if the question is not found in any document, return the refusal template exactly; if the answer would require combining sources, refuse; if any hedging or external inference is detected, reject and return the refusal template."
