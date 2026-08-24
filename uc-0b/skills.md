# skills.md

skills:
  - name: retrieve_policy
    description: Opens and loads a policy document from the specified text file.
    input: File path to the source policy (.txt).
    output: The full text of the policy document as a string.
    error_handling: Raise an error if the file cannot be found or read.

  - name: summarize_policy
    description: Takes the raw policy text and leverages an LLM to generate a compliant, structured summary adhering strictly to the enforcement rules.
    input: The full text of the policy document.
    output: A newly formulated text summary that does not omit clauses or soften obligations.
    error_handling: If the text is empty or the API fails, return an error representation string or fall back to a mock summary.
