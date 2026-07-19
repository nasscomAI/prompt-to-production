skills:
  - name: retrieve_policy
    description: Loads an employee policy text file and parses it into structured numbered clauses.
    input: Absolute path to the policy file (string).
    output: A dictionary mapping section numbers (strings) to their corresponding text content (strings).
    error_handling: Raises a FileNotFoundError if the specified file does not exist, or returns an empty dictionary.

  - name: summarize_policy
    description: Generates a summary for the policy clauses that strictly preserves all conditions and lists all clauses.
    input: A dictionary of policy sections/clauses (keys: section numbers, values: clause texts).
    output: A string containing the formatted summary matching the RICE enforcement guidelines.
    error_handling: Verifies that all 10 key obligations are included in the generated output. If a clause has complex conditions, it will fall back to quoting it verbatim to avoid meaning loss.
