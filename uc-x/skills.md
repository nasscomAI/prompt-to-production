skills:
  - name: retrieve_documents
    description: Safely maps the three internal structural policy files into indexed sections for safe retrieval operations.
    input: Paths to the available policy `.txt` files in the data directory.
    output: An indexed storage format mapping precise section numbers to unmodified chunks of source text.
    error_handling: Halts indexation gracefully via an error printout if it fails to locate the mandatory text files.

  - name: answer_question
    description: Resolves a user query by safely fetching from the indexed knowledge base without synthesizing or hallucinating text.
    input: User prompt (string).
    output: A pure single-source text answer suffixed with `[source document + section #]`, OR the predefined refusal template.
    error_handling: Bypasses hedging completely by instantly returning the predefined refusal template if a definitive single-page answer cannot be extracted.
