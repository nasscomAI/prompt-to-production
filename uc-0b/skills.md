skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: File path to the .txt policy document (string).
    output: Dictionary or list of structured sections with clause numbers and content.
    error_handling: Raises FileNotFoundError if file does not exist; raises ValueError if file is not a .txt file or cannot be parsed into sections.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary with clause references, ensuring no clause omission, obligation softening, or scope bleed.
    input: Structured sections from retrieve_policy (dict or list).
    output: String summary that includes all required clauses with preserved conditions and verbatim quotes where needed.
    error_handling: Raises ValueError if required clauses are missing from input sections or if summarization cannot preserve meaning without loss.
