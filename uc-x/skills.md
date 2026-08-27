skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes their content by document name and section number.
    input: List of paths to the policy text files (list of strings).
    output: A structured index (dictionary or object) containing text mapped to document name and section number.
    error_handling: Halts execution if any document cannot be read or parsed properly.

  - name: answer_question
    description: Searches indexed documents and returns a single-source answer with citation, or the exact refusal template.
    input: The user's question (string) and the structured index from retrieve_documents.
    output: A string containing the exact answer with citation, or the exact refusal template.
    error_handling: If the answer cannot be confidently answered from a single source without blending or hallucination, it returns the exact refusal template.
