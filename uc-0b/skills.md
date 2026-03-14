skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as a clean structured representation.
    input: File path to the `.txt` policy document.
    output: String containing the raw extracted text of the document.
    error_handling: Throws a FileNotFoundError if the document is missing.

  - name: summarize_policy
    description: Takes structured policy sections and produces a legally compliant summary extracting the 10 target clauses without meaning loss.
    input: Raw document text string.
    output: A compiled string detailing the exact summary with explicit references to the original clauses.
    error_handling: Notifies user if one of the 10 mandatory clauses could not be located in the text.
