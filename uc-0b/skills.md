# skills.md

skills:
  - name: retrieve_policy
    description: Loads the .txt policy file and returns the content as structured numbered sections.
    input: String input_path to the source txt file.
    output: A string containing the full policy text.
    error_handling: Raise a FileNotFoundError if the document cannot be located or read.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with exact clause references, enforcing multi-condition preservation.
    input: A string containing the policy text.
    output: A string containing the compliant summary with bracketed clause numbers (e.g., [2.3]).
    error_handling: Fail generation if any of the mandatory clauses are omitted or if the summary introduces hallucinated scope bleed.
