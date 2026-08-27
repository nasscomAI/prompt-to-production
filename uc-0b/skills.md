skills:
  - name: retrieve_policy
    description: Reads the raw policy text file and parses it line-by-line into structured sections.
    input: The path to the text file (`input_path`).
    output: A dictionary mapping clause numbers (e.g. "2.3") to their complete multi-line content.
    error_handling: Raises FileNotFoundError if the input file does not exist.

  - name: summarize_policy
    description: Extracts the 10 target clauses, cleans the text structure, prepends verification flags, and writes the output verbatim list to a text file.
    input: A dictionary of parsed clauses, and the path to write the output file (`output_path`).
    output: Writes a text file containing the verbatim text of all 10 clauses.
    error_handling: Validates that all 10 target clauses are present in the parsed input dictionary; raises ValueError if any target clause is missing.
