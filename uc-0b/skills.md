skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and extracts content as structured, numbered sections to ensure ground truth mapping.
    input: Absolute path to the .txt policy file (string).
    output: A structured object where keys are clause numbers and values are the verbatim text content (JSON/object).
    error_handling: Return an error if the file is missing, empty, or lacks the explicitly required numbered clauses.

  - name: summarize_policy
    description: Generates a high-fidelity summary of structured sections, ensuring inclusion of all 10 critical clauses without condition-dropping or scope bleed.
    input: Structured sections object (JSON/object).
    output: A compliant markdown summary with explicit references to all 10 core clauses (string).
    error_handling: Refuse to summarize if critical 2.x and 5.x clauses are missing; quote verbatim if summarization causes meaning loss.
