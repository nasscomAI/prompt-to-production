skills:
  - name: retrieve_policy
    description: Loads a policy text file and parses it into structured, numbered sections mapped by clause ID.
    input: Path to the policy text file (string).
    output: A dictionary mapping section numbers (e.g., '1.1', '2.3') to their corresponding raw text (dictionary of string to string).
    error_handling: Raises FileNotFoundError if the input file does not exist, or ValueError if the format does not contain numbered sections.

  - name: summarize_policy
    description: Takes structured numbered sections and produces a summary that contains every clause, using exact verbatim quotes and flags for critical binding obligations to avoid meaning changes or condition drops.
    input: Dictionary mapping clause IDs to raw text.
    output: Formatted summary text (string) containing every numbered clause.
    error_handling: If a clause contains critical conditions that are dropped or softened, quotes the clause verbatim and prepends a warning flag.
