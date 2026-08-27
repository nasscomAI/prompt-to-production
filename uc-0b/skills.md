skills:
  - name: retrieve_policy
    description: Loads a plain-text policy document and parses it into a dictionary of structured numbered sections and clauses.
    input: filepath (str) - Absolute or relative path to the policy .txt file.
    output: dict - Mapping of clause numbers (str) to their corresponding raw text (str).
    error_handling: Returns an empty dictionary if the input file does not exist, is empty, or cannot be read.

  - name: summarize_policy
    description: Analyzes the structured clauses, validates safety requirements, and produces a meaning-preserving summary of the 10 target clauses, quoting verbatim and flagging any clause that fails safety checks.
    input: clauses (dict) - Mapping of clause numbers to their raw text.
    output: str - Multi-line string containing the final verified summary of the policy clauses.
    error_handling: Appends a flagged error entry for any required clause that is missing from the input data.
