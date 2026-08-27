skills:
  - name: retrieve_policy
    description: Loads a policy text file and parses its contents into structured numbered sections for downstream processing.
    input: A string representing the absolute or relative file path to the policy text file.
    output: A dictionary or object mapping clause numbers/sections to their corresponding text contents.
    error_handling: If the file is not found or cannot be read, raise a FileNotFoundError and log a clear error message.

  - name: summarize_policy
    description: Generates a high-fidelity summary of the structured policy sections, strictly enforcing all constraints, conditions, and clause mappings.
    input: A dictionary of structured policy sections.
    output: A string containing the final summary text with all clause references preserved and no meaning loss.
    error_handling: If any required clause is missing from the input, or if a clause is ambiguous, quote the original clause verbatim, flag it, and continue processing.
