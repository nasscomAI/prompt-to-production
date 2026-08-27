skills:
  - name: retrieve_documents
    description: Load the three policy files, parse numbered sections, and index them by document name and section number.
    input: "Three policy text files in the data/policy-documents directory."
    output: "A dictionary keyed by document name, with each document mapping to a section-numbered text index."
    error_handling: "If a policy file is missing or unreadable, raise a clear error and do not continue with a partial index."

  - name: answer_question
    description: Match a user question to a single policy section and return a single-source answer with citation or a refusal if the question is out of scope.
    input: "A user question string and the indexed policy sections."
    output: "A plain-language answer string with a source citation or the exact refusal template."
    error_handling: "If the question cannot be answered from one document without blending, refuse instead of guessing or hedging; do not cite multiple documents for one answer."
