# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number for fast lookup.
    input: A list of file paths to the three policy documents.
    output: A dictionary keyed by document name, containing a nested dictionary of section numbers to clause text. Also stores full-text per document for keyword search.
    error_handling: If any file is not found, prints error to stderr and exits with code 1. If a file has no recognizable section/clause structure, loads it as raw text with a warning.

  - name: answer_question
    description: Takes a user question, searches the indexed documents for relevant sections, and returns a single-source answer with citation or the refusal template.
    input: question (str), document_index (dict as returned by retrieve_documents).
    output: A formatted answer string containing either (1) the answer text + [Source: document_name, Section X.Y] or (2) the refusal template verbatim.
    error_handling: If question is empty, prompts user to ask a question. If multiple documents are relevant, selects the most directly relevant one and answers from that single source only — never blends. If genuinely ambiguous between documents, uses refusal template.
