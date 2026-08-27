skills:
  - name: retrieve_policy
    description: Read the input policy text file and parse its content into structured numbered sections.
    input: Path to the input policy text file (string).
    output: A dictionary mapping clause/section numbers (string) to their raw text content (string).
    error_handling: If the file does not exist, raise FileNotFoundError. If the file is empty or lacks parseable clause numbers, raise ValueError.

  - name: summarize_policy
    description: Analyze structured policy sections and generate a precise summary preserving target clause obligations and conditions.
    input: A dictionary of structured sections and a list of target clause numbers.
    output: A formatted string summary where each target clause is summarized, or quoted verbatim with a flag if it is too complex.
    error_handling: If a target clause is missing from the input, or cannot be summarized without losing original meaning, raise ValueError or fall back to quoting the original clause verbatim and appending a warning flag.

