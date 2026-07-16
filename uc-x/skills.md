# skills.md

skills:
  - name: retrieve_documents
    description: Loads all three policy files from disk and returns them as a dict keyed by filename.
    input: None — file paths are fixed constants defined in app.py.
    output: dict[str, str] mapping filename → full document text (UTF-8).
    error_handling: Raises FileNotFoundError with the missing path if any document is absent.

  - name: answer_question
    description: Searches the loaded documents and returns a single-source policy answer with citation, or the exact refusal template if the question is not covered.
    input: question (str) — the employee's natural-language question; docs (dict[str, str]) — output of retrieve_documents; client (anthropic.Anthropic) — authenticated API client.
    output: str — either a policy answer ending with "Source: <filename>, Section <number>" or the verbatim refusal template.
    error_handling: Propagates anthropic.APIError on API failure; never swallows errors silently.
