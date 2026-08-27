skills:
  - name: retrieve_policy
    description: Loads a text-based policy file and parses its contents into structured numbered sections for downstream summarization.
    input: Path to the policy text file as a string.
    output: A dictionary mapping clause numbers (e.g., '2.3', '5.2') to their raw text content.
    error_handling: If the file is missing or unreadable, the skill logs an error and raises FileNotFoundError.

  - name: summarize_policy
    description: Summarizes the structured policy sections, ensuring all 10 target clauses are preserved with binding verbs and multi-conditions intact.
    input: A dictionary of structured sections from the policy.
    output: A string containing the compliant summary text with clear clause references.
    error_handling: If any of the 10 critical clauses are missing in the input structure, they are flagged as missing, and their text is retrieved verbatim if possible.
