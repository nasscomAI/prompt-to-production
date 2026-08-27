# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as a dictionary of structured numbered sections.
    input: File path (string) to a .txt policy document.
    output: A dictionary where keys are clause numbers (e.g., "2.3") and values are the corresponding clause text.
    error_handling: Return an error message if the file is not found, cannot be read, or does not contain recognizable numbered sections.

  - name: summarize_policy
    description: Processes structured policy sections to produce a compliant summary that strictly adheres to the original clauses and conditions.
    input: A dictionary of structured numbered sections (output from retrieve_policy).
    output: A formatted text summary where each entry includes the original clause number and a strictly compliant summary or verbatim quote.
    error_handling: Flag sections that cannot be summarized without loss of meaning; refuse to process if the input dictionary is empty.
