# skills.md

skills:
  - name: retrieve_documents
    description: Loads the 3 specified policy files and structurally indexes them by document name and section number for precise citation lookup.
    input: File paths to the HR, IT, and Finance policy texts.
    output: A parsed structure/dictionary linking each specific section number to its exact textual content and document origin.
    error_handling: Raises an explicit error if the files cannot be found or read properly.

  - name: answer_question
    description: Evaluates an incoming question against the parsed index, providing an explicitly cited single-source answer or falling back to a hardcoded refusal template gracefully.
    input: The indexed document data from retrieve_documents and a user question string.
    output: A direct answer string terminating with a citation `(Source: doc_name, Section X.X)`, OR the exact verbatim refusal template.
    error_handling: If the query matches elements spanning across two separate files producing a blend, or lacks sufficient matches entirely, the system intercepts and reliably returns the exact refusal template without hallucinating.
