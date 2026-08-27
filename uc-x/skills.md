skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes content by document name and section number.
    input: Directory path containing the 3 policy text files.
    output: Dictionary keyed by document name, with sections as sub-keys and text as values.
    error_handling: If any policy file is missing, print a warning and continue with remaining files. Never silently skip.

  - name: answer_question
    description: Searches indexed documents for the most relevant single-source answer and returns it with citation or refusal template.
    input: User question as string, indexed documents dictionary.
    output: Answer string with citation (document name + section number), or exact refusal template if not found.
    error_handling: If question matches content in more than one document ambiguously, use refusal template rather than blending answers.
