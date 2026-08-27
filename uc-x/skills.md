skills:
  - name: retrieve_documents
    description: Loads and indexes all three policy files (HR, IT, Finance) by section numbers and content.
    input: Path to the directory containing policy files (string).
    output: A dictionary mapping tuples of (document_name, policy_ref, section_num) to section text.
    error_handling: Raises a FileNotFoundError if any of the files are missing or inaccessible.

  - name: answer_question
    description: Processes a user's question, searches the indexed documents, and returns a single-source answer with citations or the refusal template.
    input: A string representing the user's question.
    output: A string containing the answer and citation, or the exact refusal template.
    error_handling: Refuses to combine multiple sources, avoids hedging, and prints the exact refusal template for out-of-scope queries.
