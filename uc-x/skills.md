skills:
  - name: retrieve_documents
    description: Loads all 3 core policy text files into systemic lookup layers mapped by filename and operational keys.
    input: None.
    output: String blocks indexed directly by policy source targets.
    error_handling: System terminates execution cleanly if files are missing from the data path.

  - name: answer_question
    description: Processes individual user interactive questions and evaluates single-source boundaries or structural refusals.
    input: String question from the user terminal.
    output: High-fidelity citation text block or the official verbatim refusal payload string.
    error_handling: Defaults directly to the required structural refusal template if ambiguous or non-explicit data is matched.
