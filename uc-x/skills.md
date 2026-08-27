# skills.md

skills:
  - name: retrieve_documents
    description: Loads policy files (HR, IT, Finance) and parses their structured text into an indexed catalog by document name and section number.
    input: A list of file paths to policy text documents.
    output: A dictionary mapping document names and section numbers to the exact text contents.
    error_handling: System exits or prints an error if a designated file is fundamentally corrupted or missing.

  - name: answer_question
    description: Searches the indexed documents for explicit answers, rejecting multi-document blending and strictly applying refusal templates if missing or ambiguously split.
    input: The indexed document dictionary and a user query string.
    output: A single-source answer string accompanied by exact document and section citations, or the specified strict refusal template.
    error_handling: Safely uses the exact refusal template verbatim instead of crashing or hallucinating if the mapping confidence is low.
