skills:
  - name: retrieve_documents
    description: Explicitly loads all three policy text files and structures their specific contents uniquely by document name and section number.
    input:
      type: list
      format: An array of file paths corresponding to the specific policy documents to analyze.
    output:
      type: dict
      format: A multi-level structured cache associating each internal paragraph securely and permanently with its native section identifier and overarching document title.
    error_handling: It rejects incomplete structural inputs explicitly, ensuring no silent condition dropping occurs during indexing.

  - name: answer_question
    description: Queries indexed document caches to generate a purely single-source answer accompanied exactly by its section citation, or refuses securely.
    input:
      type: dict
      format: Parameters comprising the explicit string question and the indexed structural document cache.
    output:
      type: string
      format: A strictly bounded response sentence containing its specific document citation, or the required verbatim refusal template.
    error_handling: To permanently prevent cross-document blending, it unconditionally refuses if solving the query requires synthesizing multiple files; to block hedged hallucinations, it replaces any uncertainty immediately with the exact verbatim refusal template without engaging in assumptions.
