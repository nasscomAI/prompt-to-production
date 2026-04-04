# skills.md

skills:
  - name: "retrieve_documents"
    description: "Loads and indexes all available policy text files, creating a searchable map of document names and section numbers."
    input: "A list of .txt file paths."
    output: "An indexed collection of policy sections and clauses."
    error_handling: "If a required document is missing, the system must not attempt to answer questions related to that domain."

  - name: "answer_question"
    description: "Performs targeted search within the indexed policies to find the single most relevant source, returning a cited answer or the refusal template."
    input: "A user query (text string)."
    output: "A grounded response citing [Doc Name, Section] OR the exact standardized refusal template."
    error_handling: "If a query triggers multiple conflicting interpretations across documents, the system must refuse and point to the relevant department."
