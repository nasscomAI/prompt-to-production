# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document key.
    input: base directory containing the 3 policy .txt files.
    output: dict {doc_key: raw_text} for HR, IT, and FINANCE.
    error_handling: >
      Raises FileNotFoundError (surfaced as a clean CLI message, exit 1) if any of the
      three policy files is missing, rather than answering from a partial corpus.

  - name: answer_question
    description: Returns a single-source, cited answer or the verbatim refusal template.
    input: a free-text question string.
    output: >
      "<answer>\n(Source: <document>, section N.M)" from exactly one document, OR the
      exact refusal template when nothing matches.
    error_handling: >
      Empty question or no matching intent → refusal template. If the top-scoring
      intents come from more than one document (genuine cross-document ambiguity) →
      refusal template. Never blends documents and never emits hedging phrases.
