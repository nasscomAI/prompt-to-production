# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns the content grouped into structured numbered sections.
    input: File path (string) to the policy document.
    output: A dictionary mapping section numbers to clause text (dict).
    error_handling: Raises FileNotFoundError if the file cannot be read.

  - name: summarize_policy
    description: Takes the structured sections and produces a compliant summary that strictly follows the enforcement rules, referencing the original clause numbers.
    input: Structured sections (dict) from retrieve_policy.
    output: A summary string (string).
    error_handling: Return error message string if inputs are empty or malformed.
