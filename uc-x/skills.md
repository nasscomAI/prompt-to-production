# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    input: Optional path to the policy-documents folder; defaults to ../data/policy-documents relative to app.py.
    output: Index of clause entries, each with document name, section number, section title, full clause text, and pre-tokenised search words (with domain abbreviations like LWP expanded).
    error_handling: Missing or unreadable document files are reported by name on stderr and the run exits with code 1 rather than answering from a partial corpus.

  - name: answer_question
    description: Searches the indexed documents and returns a single-source answer with citation, or the exact refusal template.
    input: question (string) and the document index from retrieve_documents.
    output: The best-matching single clause quoted verbatim prefixed with nothing and followed by "[Source: <document>, section <number>]" — or the refusal template exactly as defined in agents.md when no clause matches at least 2 distinct content terms covering at least half of the question's content terms.
    error_handling: Weak or ambiguous matches are refused, never guessed; empty or stop-word-only questions get the refusal template; only one clause from one document is ever returned, so cross-document blending is structurally impossible.
