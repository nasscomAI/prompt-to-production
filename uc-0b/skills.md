# skills.md

skills:

  - name: retrieve_policy
    description: Load a plaintext policy file and extract its content into structured, numbered sections.
    input: A string representing the absolute or relative file path to the policy text file.
    output: A dictionary mapping section numbers (e.g., '2.3', '5.2') to their raw text content.
    error_handling: Raise FileNotFoundError if the file does not exist, and ValueError if the document is formatted incorrectly or cannot be parsed.

  - name: summarize_policy
    description: Process structured policy sections and generate a compliant summary that preserves all obligations, conditions, and clause references.
    input: A dictionary mapping section numbers to raw clause text content.
    output: A formatted summary string where every required clause (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) is summarized with its clause reference, preserving all conditions.
    error_handling: Raise ValueError if any of the required 10 clauses are missing from the input, or if the summary would drop conditions or soften obligations.
