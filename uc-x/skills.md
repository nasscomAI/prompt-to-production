skills:
  - name: retrieve_documents
    description: Loads all 3 policy .txt files and indexes their content by document name and section number.
    input: A list of file paths to the 3 policy documents.
    output: A list of dicts, each with keys doc_name (str, e.g. "policy_it_acceptable_use.txt"), section (str, e.g. "3.1"), and text (str, the section's full text).
    error_handling: If any of the 3 files does not exist or cannot be read, raises a clear error naming the missing path rather than silently indexing fewer documents.

  - name: answer_question
    description: Searches the indexed documents for a question and returns a single-source answer with citation, or the exact refusal template.
    input: question (str) and the indexed sections list from retrieve_documents.
    output: A string — either "Per <doc_name> section <section>: <text>" for a single-source match, or the exact refusal template verbatim.
    error_handling: If no section matches the question, or matching sections span more than one document, returns the exact refusal template rather than guessing or blending across documents.
