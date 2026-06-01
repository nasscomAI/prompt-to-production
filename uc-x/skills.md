skills:
  - name: retrieve_documents
    description: Loads the three target policy documents and parses their contents into a structured index organized by document name and section number.
    input: None (retrieves from pre-defined paths under `../data/policy-documents/`).
    output: A dictionary/structured collection of sections indexed by document name and section number, containing the literal section text.
    error_handling: Raises an `IOError` with a clear message if any of the three required policy files are missing or unreadable.

  - name: answer_question
    description: Searches the indexed policy documents for the user's query to return a precise, single-source answer with exact citations, or returns the verbatim refusal template if not fully covered.
    input: A user query string (e.g., "Can I carry forward unused annual leave?") and the parsed documents index from `retrieve_documents`.
    output: A factual answer string containing a single-source policy explanation and explicit document/section citations, or the exact verbatim refusal template.
    error_handling: Returns the exact refusal template (referencing missing policy coverage) if the query is ambiguous, not fully covered, requires cross-document blending, or if the input query is empty or invalid.

