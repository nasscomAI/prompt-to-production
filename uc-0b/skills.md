skills:
  - name: retrieve_policy
    description: Loads a policy text file and parses it into structured sections with headers and clauses.
    input: input_path (str) to the employee leave policy text file.
    output: A structured string or dictionary representing the policy sections.
    error_handling: Raises FileNotFoundError if the input file does not exist, and prints a warning for completely empty inputs.

  - name: summarize_policy
    description: Uses Gemini model to generate a strict summary of the policy document while adhering to the agents.md RICE rules.
    input: structured_policy (str) - the policy text to summarize.
    output: A summary (str) containing all key clauses with exact conditions preserved.
    error_handling: If the API call fails, falls back to a safe default warning summary and flags all critical clauses for manual review.
