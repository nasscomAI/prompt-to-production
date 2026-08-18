skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes their content by document name and section number.
    input: "dir_path or list of file paths (the 3 .txt policy files)."
    output: "list of dicts, each with keys: doc_name (str, e.g. 'policy_it_acceptable_use.txt'), section (str, e.g. '3.1'), text (str, full section text with wrapped lines joined)."
    error_handling: "Raises FileNotFoundError if any of the 3 expected files is missing. A document with no parseable numbered sections contributes zero index entries rather than raising."

  - name: answer_question
    description: Searches the indexed documents for the question and returns a single-source answer with citation, or the refusal template.
    input: "question (str), index (list of dicts from retrieve_documents)."
    output: "str — either 'Source: <doc_name> Section <n>' followed by the answer text, or the exact refusal template."
    error_handling: "If no section scores above zero relevance, or if two different documents score comparably (genuine ambiguity), returns the exact refusal template rather than guessing or blending."
